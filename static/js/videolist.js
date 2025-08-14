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
                loadVideos(savedBookId);
            }
        }).fail(function() {
            console.error('加载书单失败');
        });
    }

    // 加载视频数据
    function loadVideos(bookId, page = 1) {
        $.get(`/get_videos/${bookId}`, {page: page, per_page: 10}, function(data) {
            const tbody = $('#videosTable tbody');
            tbody.empty();
            
            // 更新分页信息
            $('#startRecord').text((data.page - 1) * data.per_page + 1);
            $('#endRecord').text(Math.min(data.page * data.per_page, data.total));
            $('#totalRecords').text(data.total);
            
            // 渲染分页控件
            renderVideosPagination(data.page, data.total_pages);
            
            data.data.forEach(video => {
                const videoUrls = video.video_urls ? video.video_urls.split(',') : [];
                const videoStatuses = video.video_statuses ? video.video_statuses.split(',') : [];
                
                const videoCells = videoUrls.map((url, index) => {
                    const status = index < videoStatuses.length ? videoStatuses[index] : '0';
                    return renderVideoCell(url, video.image_id, status);
                }).join('');

                const row = `
                    <tr data-video-id="${video.video_id}">
                        <td>${video.image_id}</td>
                        <td>${video.paragraph_initial || ''}</td>
                        <td>
                            <div class="d-flex flex-wrap gap-2">
                                ${videoCells}
                            </div>
                            <div class="d-flex flex-wrap gap-2">
                                ${renderStatusCheckboxes(videoUrls, videoStatuses, video.video_id)}
                            </div>                            
                        </td>
                    </tr>
                `;
                tbody.append(row);
            });

            // 绑定状态checkbox事件
            $('.video-status-checkbox').change(updateVideoStatus);
            // 绑定删除按钮事件
            $(document).on('click', '.delete-btn', function() {
                const videoUrl = $(this).data('url');
                deleteVideo(videoUrl);
            });
        });
    }

    // 渲染视频分页控件
    function renderVideosPagination(currentPage, totalPages) {
        const pagination = $('#videosPagination');
        pagination.empty();

        // 上一页按钮
        pagination.append(`
            <li class="page-item ${currentPage <= 1 ? 'disabled' : ''}" id="prevPage">
                <a class="page-link" href="#" data-page="${currentPage - 1}">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            </li>
        `);

        // 页码按钮
        for (let i = 1; i <= totalPages; i++) {
            pagination.append(`
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `);
        }

        // 下一页按钮
        pagination.append(`
            <li class="page-item ${currentPage >= totalPages ? 'disabled' : ''}" id="nextPage">
                <a class="page-link" href="#" data-page="${currentPage + 1}">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            </li>
        `);

        // 绑定分页事件
        $('.page-link').off('click').on('click', function(e) {
            e.preventDefault();
            const page = $(this).data('page');
            const bookId = $('#bookSelect').val();
            if (bookId) {
                loadVideos(bookId, page);
            }
        });
    }

    // 渲染视频单元格
    function renderVideoCell(url, imageId, status) {
        if (!url) return '';
        
        const fullUrl = `${COMFYUI_URL}/view?filename=${url}`;
        return `
            <div class="video-thumbnail-container">
                <video src="${fullUrl}" 
                     class="video-thumbnail img-thumbnail" 
                     data-url="${url}"
                     data-image-id="${imageId}"
                     style="width:200px; height:266px;"
                     controls>
                </video>
            </div>
        `;
    }

    // 渲染状态checkbox
    function renderStatusCheckboxes(urls, statuses, videoId) {
        return urls.map((url, index) => {
            const status = index < statuses.length ? statuses[index] : '0';
            return `
                <div class="form-statustitle">是否选中：
                    <input class="form-check-input video-status-checkbox" 
                           type="checkbox" 
                           data-url="${url}"
                           ${status === '1' ? 'checked' : ''}>
                    &nbsp;&nbsp;&nbsp;&nbsp;
                    <button class="btn btn-danger btn-sm delete-btn" 
                        data-video-id="${videoId}" 
                        data-url="${url}">删除</button>
                </div>
            `;
        }).join('');
    }

    // 更新视频状态
    function updateVideoStatus() {
        const checkbox = $(this);
        const url = checkbox.data('url');
        const value = checkbox.is(':checked') ? '1' : '0';
        
        $.ajax({
            url: '/update_video_status',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                video_url: url,
                value: value
            }),
            success: function() {
                console.log('视频状态更新成功');
            }
        });
    }

    // 删除视频
    function deleteVideo(video_url) {
        if (confirm('确定要删除这条记录吗？')) {
            $.ajax({
                url: '/delete_video',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    url: video_url
                }),
                success: function() {
                    console.log('视频删除成功');
                    // 删除成功后刷新列表
                    const bookId = $('#bookSelect').val();
                    if (bookId) {
                        loadVideos(bookId);
                    }
                },
                error: function() {
                    console.error('删除失败');
                    alert('删除失败');
                }
            });
        }
    }

    // 页面加载时初始化
    loadBooklists();

    // 书单选择变化事件
    $('#bookSelect').change(function() {
        const bookId = $(this).val();
        if (bookId) {
            setCookie('selectedBookId', bookId, 7); // 保存7天
            loadVideos(bookId);
        } else {
            document.cookie = 'selectedBookId=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            $('#videosTable tbody').empty();
        }
    });

});
