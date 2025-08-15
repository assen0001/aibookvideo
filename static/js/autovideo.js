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
     
     // 显示模态框
    $('#bookModal').modal('show');
    
    // 一键生成视频按钮点击事件
    $('#btnSave').click(function() {
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
        
        // 禁用按钮防止重复提交
        const $btn = $(this);
        const originalText = $btn.text();
        $btn.prop('disabled', true).text('生成中...');
        
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
                    
                    // 调用外部API
                    const apiUrl = `${N8N_URL}/webhook/160cb42d-2ee6-4486-9d30-105e8e361f45?book_id=${book_id}`;
                    
                    $.get(apiUrl, function(result) {
                        console.log('API调用完成:', result);
                        // 可以在这里添加成功后的处理逻辑
                    }).fail(function() {
                        console.error('API调用失败');
                        alert('视频生成请求发送失败');
                    });
                } else {
                    alert('创建书单失败: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('创建书单失败:', error);
                alert('创建书单失败: ' + error);
            },
            complete: function() {
                // 恢复按钮状态
                $btn.prop('disabled', false).text(originalText);
            }
        });
    });
});
