// 日期格式化函数
function formatDateTime(dateStr) {
    // 创建Date对象，然后减去8小时（8 * 60 * 60 * 1000 毫秒）
    const date = new Date(new Date(dateStr).getTime() - 8 * 60 * 60 * 1000);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

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
    
    // Cookie操作函数
    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = "expires=" + date.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i=0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length);
        }
        return null;
    }

    // 加载书单数据
    function loadBooklists() {
        $.get('/get_booklists', function(data) {
            const bookSelect = $('#bookSelect');
            bookSelect.empty();
            bookSelect.append('<option value="">-- 请选择 --</option>');
            data.forEach(book => {
                bookSelect.append(`<option value="${book.id}">${book.book_name}</option>`);
            });

            // 加载完成后检查是否有保存的书单选择
            const savedBookId = getCookie('selectedBookId');
            if (savedBookId) {
                bookSelect.val(savedBookId);
                loadSubtitleContent(savedBookId);
            }
        }).fail(function() {
            console.error('加载书单失败');
        });
    }

    // 加载字幕内容
    function loadSubtitleContent(bookId) {
        $.ajax({
            url: '/get_subtitle_content?book_id=' + bookId,
            type: 'GET',
            success: function(data) {
                if (data && data.paragraph_initial) {
                    $('#subtitleContent').val(data.paragraph_initial.replace(/\\n/g, '\n'));
                } else {
                    $('#subtitleContent').val('该书单暂无字幕内容');
                }
            },
            error: function() {
                alert('加载字幕内容失败');
            }
        });
    }

    
    // 提交按钮点击事件
    $('#submitBtn').click(function() {
        if (confirm('是否提交字幕转语音？')) {
            const bookId = $('#bookSelect').val();
            const voiceType = $('input[name="voiceType"]:checked').val();
            const subtitleContent = $('#subtitleContent').val();
            
            if (!bookId || !subtitleContent) {
                alert('请先选择书单并加载字幕内容');
                return;
            }

            // TODO: 调用后端接口处理字幕转语音
            console.log('提交数据:', {
                bookId: bookId,
                voiceType: voiceType,
                subtitleContent: subtitleContent
            });
        }
    });

    // 加载书单数据
    loadBooklists();

    // 加载语音列表
    function loadVoiceList(bookId) {
        if (!bookId) {
            $('#voiceListContainer').hide();
            return;
        }

        $.ajax({
            url: '/get_voice_list?book_id=' + bookId,
            type: 'GET',
            success: function(data) {
                const voiceList = $('#voiceList');
                voiceList.empty();
                
                if (data && data.length > 0) {
                    $('#voiceListContainer').show();
                    data.forEach(voice => {                        
                        console.log("日期："+voice.create_time);
                        const audioElement = `
                            <div class="mb-3 d-flex align-items-center">                                
                                <audio controls style="width:650px">
                                    <source src="/static/uploads/voice/${voice.voider_url}" type="audio/mpeg">
                                    您的浏览器不支持音频元素
                                </audio>
                                &nbsp;&nbsp;
                                是否选中：<input type="checkbox" class="form-check-input me-3" ${voice.voider_status === 1 ? 'checked' : ''} 
                                    onchange="updateVoiceStatus(${voice.id}, this.checked ? 1 : 0)">
                                &nbsp;&nbsp;
                                生成时间：<small class="text-muted ms-3">${formatDateTime(voice.create_time)}</small>
                                &nbsp;&nbsp;&nbsp;&nbsp;
                                <button class="btn btn-danger btn-sm" onclick="deleteVoice(${voice.id})">删除</button>
                                &nbsp;&nbsp;&nbsp;&nbsp;
                                <button class="btn btn-primary btn-sm" onclick="downloadVoice(${voice.id}, '${voice.voider_url}')">下载</button>
                            </div>
                        `;
                        voiceList.append(audioElement);
                    });
                } else {
                    $('#voiceListContainer').hide();
                }
            },
            error: function() {
                console.error('加载语音列表失败');
            }
        });
    }

    // 书单选择变化事件
    $('#bookSelect').change(function() {
        const bookId = $(this).val();
        if (bookId) {
            loadSubtitleContent(bookId);
            loadVoiceList(bookId);
        } else {
            $('#subtitleContent').val('');
            $('#voiceListContainer').hide();
        }
    });

    // 初始化时加载语音列表（如果有选中的书单）
    const savedBookId = getCookie('selectedBookId');
    if (savedBookId) {
        loadVoiceList(savedBookId);
    }

    // 更新语音状态
    window.updateVoiceStatus = function(voiceId, status) {
        $.ajax({
            url: '/update_voice_status',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                voice_id: voiceId,
                status: status
            }),
            success: function() {
                console.log('语音状态更新成功');
            },
            error: function(xhr, status, error) {
                console.error('语音状态更新失败:', error);
                alert('语音状态更新失败，请重试');
            }
        });
    }

    // 删除语音
    window.deleteVoice = function(voiceId) {
        if (confirm('确定要删除这条语音吗？')) {
            $.ajax({
                url: '/delete_voice',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    voice_id: voiceId
                }),
                success: function() {
                    // 重新加载语音列表
                    const bookId = $('#bookSelect').val();
                    loadVoiceList(bookId);
                    console.log('语音删除成功');
                },
                error: function(xhr, status, error) {
                    console.error('语音删除失败:', error);
                    alert('语音删除失败，请重试');
                }
            });
        }
    }

    // 下载语音
    window.downloadVoice = function(voiceId, filename) {
        const link = document.createElement('a');
        link.href = `/static/uploads/voice/${filename}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

});
