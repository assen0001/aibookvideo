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
     const COMFYUI_URL = config.COMFYUI_URL;
     const COQUITTS_URL = config.COQUITTS_URL;
     const AIBOOKVIDEO_URL = config.AIBOOKVIDEO_URL;
     
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
                const book_id = response.book_id;                
                // 显示视频生成中提示
                $('#videoStatus').show();                
                // 更新状态文本
                $('#videoStatus').find('#status-text').text('发送视频生成请求...');
                $('#videoStatus').find('#progressPercent').text('0%');
                // $('#statusMessages').html('');
                
                // 调用外部API
                const apiUrl = `${N8N_URL}/webhook/160cb42d-2ee6-4486-9d30-105e8e361f45`;           
                $.post(apiUrl, { 
                    book_id: book_id,
                    aibookvideo_url: AIBOOKVIDEO_URL,
                    n8n_url: N8N_URL,
                    comfyui_url: COMFYUI_URL,
                    coquitts_url: COQUITTS_URL,
                }, function(result) {
                    console.log('API调用完成:', result);                    
                    checkVideoStatus(book_id);  // 执行定时刷新任务
                }).fail(function() {
                    console.error('API调用失败');
                    alert('视频生成请求发送失败');
                    $('#videoStatus').hide();
                    // 错误时恢复按钮状态
                    $btn.prop('disabled', false);
                    $btn.find('.btn-text').show();
                    $btn.find('.btn-loader').hide();
                });                
            },
            complete: function() {
                // 请求完成后保持按钮禁用状态，显示完成信息
                // $btn.find('.btn-text').text('已提交生成');
                // $btn.find('.btn-loader').hide();      
                console.log('执行定时刷新任务');        
            }
        });
    });

    // 初始化时检查状态：0-表示查询表ai_jobonline中当前任务
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
                    $('#progressPercent').text('30%');
                } else if (jobs[jobs.length - 1].job_type === 4) {
                    $('#progressPercent').text('50%');
                } else if (jobs[jobs.length - 1].job_type === 5) {
                    $('#progressPercent').text('70%');
                } else if (jobs[jobs.length - 1].job_type === 6) {
                    $('#progressPercent').text('90%');
                } 
                
                // 检查是否有任务失败
                if ([3, 4, 5].includes(jobs[0].job_status)) {
                    $('#status-text').text('视频生成失败');
                     htmlContent += `                      
                     <div>
                        <button id="continueBtn" class="btn btn-primary btn-sm">继续执行</button>
                     </div>
                     `;
                    $('#statusMessages').html(htmlContent);
                    $('#continueBtn').on('click', function() {
                        if (!confirm('确定要重做吗？')) {return}
                        // 异步发送POST请求
                        fetch(`${N8N_URL}/webhook/160cb42d-2ee6-4486-9d30-105e8e361f45`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                redo: 'on',
                                book_id: jobs[0].book_id,
                                aibookvideo_url: AIBOOKVIDEO_URL,
                                n8n_url: N8N_URL,
                                comfyui_url: COMFYUI_URL,
                                coquitts_url: COQUITTS_URL,
                            })
                        }).catch(error => console.error('请求失败:', error));
                        
                        // 立即调用状态检查函数
                        checkVideoStatus(jobs[0].book_id);
                    });
                    // return; // 终止轮询
                }
               
                // 10秒后再次查询
                setTimeout(() => checkVideoStatus(jobs[0].book_id), 10000);
            }
        }).fail(function() {
            console.error('没有任务状态数据');
            $('#status-text').text('没有任务状态数据');
            $('#progressPercent').text('0%');
            $('#statusMessages').html('');
        });
    }  


});
