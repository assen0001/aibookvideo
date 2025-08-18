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
        $btn.find('.btn-text').text('视频生成中');
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
                    $('#videoStatus').find('.status-text').text('正在生成视频...');
                    
                    // 调用外部API
                    const apiUrl = `${N8N_URL}/webhook/160cb42d-2ee6-4486-9d30-105e8e361f45?book_id=${book_id}`;
                    
                    $.get(apiUrl, function(result) {
                        console.log('API调用完成:', result);
                        // 更新成功状态
                        $('#videoStatus').find('.status-text').text('视频生成请求已发送');
                        $('#videoStatus').find('.status-spinner').hide();
                        $('#videoStatus').find('.status-icon').show();
                    }).fail(function() {
                        console.error('API调用失败');
                        alert('视频生成请求发送失败');
                        $('#videoStatus').hide();
                        // 错误时恢复按钮状态
                        $btn.prop('disabled', false);
                        $btn.find('.btn-text').text('一键生成视频');
                    });
                } else {
                    alert('创建书单失败: ' + response.message);
                    $('#videoStatus').hide();
                    // 错误时恢复按钮状态
                    $btn.prop('disabled', false);
                    $btn.find('.btn-text').text('一键生成视频');
                }
            },
            error: function(xhr, status, error) {
                console.error('创建书单失败:', error);
                alert('创建书单失败: ' + error);
                $('#videoStatus').hide();
                // 错误时恢复按钮状态
                $btn.prop('disabled', false);
                $btn.find('.btn-text').text('一键生成视频');
            },
            complete: function() {
                // 请求完成后保持按钮禁用状态，显示完成信息
                $btn.find('.btn-text').text('已提交生成');
                $btn.find('.btn-loader').hide();
                // 不恢复按钮状态，防止重复提交
            }
        });
    });
});
