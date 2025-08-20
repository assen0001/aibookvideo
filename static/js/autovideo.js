$(document).ready(function() {
     // 从配置读取URL
     let config = {};
     $.ajax({
         url: '/get_config',
         async: false,
         success: function(data) {
             config = data;
         }
     });

     const N8N_URL = config.N8N_URL;
    //  const COMFYUI_URL = config.COMFYUI_URL;
     
    // 实时预览更新
    $('#modalBookName, #modalBookAuthor, #modalBookNote').on('input', function() {
        const bookName = $('#modalBookName').val();
        const bookAuthor = $('#modalBookAuthor').val();
        
        if (bookName || bookAuthor) {
            $('.preview-placeholder').html(`
                <i class="fas fa-book-open"></i>
                <h5>${bookName || '未命名书籍'}</h5>
                <p>${bookAuthor || '未知作者'}</p>
                <small>准备生成视频...</small>
            `);
        } else {
            $('.preview-placeholder').html(`
                <i class="fas fa-book-open"></i>
                <h5>预览区域</h5>
                <p>填写左侧表单后，这里将显示预览</p>
            `);
        }
    });
    
    // 风格选择变化时的预览
    $('#modalBookStyler').on('change', function() {
        const style = $(this).val();
        if (style) {
            console.log('选择风格:', style);
        }
    });
    
    // 一键生成视频按钮点击事件 - 适配新的表单结构
    $('#btnGenerate').click(function(e) {
        e.preventDefault();
        // 获取表单数据
        const bookName = $('#modalBookName').val();
        const bookAuthor = $('#modalBookAuthor').val();
        const bookNote = $('#modalBookNote').val();
        const bookPrompt = $('#modalBookPrompt').val();
        const bookStyler = $('#modalBookStyler').val();
        
        // 验证必填字段
        if (!bookName || !bookAuthor) {
            alert('请填写书名和作者');
            return;
        }
        
        // 显示确认对话框
        if (!confirm('视频生成时间较长，请耐心等待，是否继续？')) {
            return;
        }
        
        // 禁用按钮防止重复提交，并显示"视频生成中"
        const $btn = $(this);
        $btn.prop('disabled', true);
        $btn.addClass('disabled'); // 添加禁用样式类
        $btn.find('.btn-text').hide();
        $btn.find('.btn-loader').show();
        
        // 准备数据
        const data = {
            book_name: bookName,
            book_author: bookAuthor,
            book_note: bookNote,
            book_supplement_prompt: bookPrompt,
            sdxl_prompt_styler: bookStyler
        };
        
        // 发送POST请求创建书单
        $.ajax({
            url: '/autovideo/create',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                if (response.status === 'success') {
                    const book_id = response.book_id;
                    
                    // 显示视频生成中提示
                    $('#videoStatus').show();
                    
                    // 更新状态文本
                    $('#videoStatus').find('#status-text').text('正在生成视频...');
                    $('#videoStatus').find('#progressPercent').text('0%');
                    $('#statusMessages').html('');
                    
                    // 调用外部API
                    const apiUrl = `${N8N_URL}/webhook/160cb42d-2ee6-4486-9d30-105e8e361f45?book_id=${book_id}`;
                    // const apiUrl = `${N8N_URL}/webhook/bf24c5d7-427b-4f63-91cc-42e004af8971?book_id=${book_id}`;  // 测试用

                    
                    $.get(apiUrl, function(result) {
                        console.log('API调用完成:', result);
                        // 执行定时刷新任务
                        checkVideoStatus(book_id);
                    }).fail(function() {
                        console.error('API调用失败');
                        alert('视频生成请求发送失败');
                        $('#videoStatus').hide();
                        // 错误时恢复按钮状态
                        $btn.prop('disabled', false);
                        $btn.find('.btn-text').show();
                        $btn.find('.btn-loader').hide();
                    });
                } else {
                    alert('创建书单失败: ' + response.message);
                    $('#videoStatus').hide();
                    // 错误时恢复按钮状态
                    $btn.prop('disabled', false);
                    $btn.find('.btn-text').show();
                    $btn.find('.btn-loader').hide();
                }
            },
            error: function(xhr, status, error) {
                console.error('创建书单失败:', error);
                alert('创建书单失败: ' + error);
                $('#videoStatus').hide();
                // 错误时恢复按钮状态
                $btn.prop('disabled', false);
                $btn.find('.btn-text').show();
                $btn.find('.btn-loader').hide();
            },
            complete: function() {
                // 请求完成后保持按钮禁用状态，显示完成信息
                // $btn.find('.btn-text').text('已提交生成');
                // $btn.find('.btn-loader').hide();
                // 不恢复按钮状态，防止重复提交
            }
        });
    });

    checkVideoStatus(0);

    // 检查视频动态状态消息显示
    function checkVideoStatus(book_id) {
        const checkUrl = `/autovideo/status?book_id=${book_id}`;
        
        $.get(checkUrl, function(response) {
            if (response.status === 'success' && response.data.length > 0) {
                const jobs = response.data;
                let htmlContent = '';
                
                // 生成状态消息
                jobs.forEach((job, index) => {
                    const statusText = {
                        1: '🔄',    // 执行中
                        2: '✅',    // 已完成
                        3: '⏳',    // 已暂停
                        4: '❌',    // 已失败
                        5: '⚠️',    // 已取消
                        6: '⏳',    // 排队中
                    }[job.job_status] || '❓'; // 未知状态
                    
                    htmlContent += `
                        <div class="status-item ${index === 0 ? 'main-status' : 'sub_status'}">
                            <span class="job-name">${job.job_name}</span>
                            <span class="job-status">${statusText}</span>
                        </div>
                    `;
                });
                
                // 更新状态显示
                $('#videoStatus').show();
                $('#statusMessages').html(htmlContent);
                $('#status-text').text('正在生成视频...');
                
                // 判断首条任务状态
                if (jobs[0].job_status === 2) {
                    $('#status-text').text('视频任务全部完成');
                    $('#progressPercent').text('100%');
                    // 设置视频完成后查看预览效果，用户点击可播放生成的视频
                    $('.preview-placeholder').html(`
                        <video controls class="preview-video">
                            <source src="/${jobs[0].videomerge_url}" type="video/mp4">
                            您的浏览器不支持 video 标签。
                        </video>
                    `);

                    return; // 终止轮询
                }

                // 这里增加判断 jobs数组末尾项目job_type的值：
                if (jobs[jobs.length - 1].job_type === 1) {
                    $('#progressPercent').text('10%');
                } else if (jobs[jobs.length - 1].job_type === 2) {
                    $('#progressPercent').text('20%');
                } else if (jobs[jobs.length - 1].job_type === 3) {
                    $('#progressPercent').text('40%');
                } else if (jobs[jobs.length - 1].job_type === 4) {
                    $('#progressPercent').text('60%');
                } else if (jobs[jobs.length - 1].job_type === 5) {
                    $('#progressPercent').text('90%');
                } else if (jobs[jobs.length - 1].job_type === 6) {
                    $('#progressPercent').text('100%');
                } 
                
                // 10秒后再次查询
                setTimeout(() => checkVideoStatus(book_id), 10000);
            }
        }).fail(function() {
            console.error('没有任务状态数据');
            $('#status-text').text('没有任务状态数据');
            $('#progressPercent').text('0%');
            $('#statusMessages').html('');
        });
    }  

});
