// Mapping between album IDs and corresponding HTML elements
var albumMap = {};

function fetchAlbums() {
    $.ajax({
        url: '/albums',  // Flask route for fetching albums
        type: 'GET',
        success: function (data) {
            createAlbumDivs(data);
        },
        error: function (xhr, status, error) {
            // Handle errors here
            console.error(xhr.responseText);
        }
    });
}

function createAlbumDivs(albums) {
    // Loop through albums and create div elements
    albums.forEach(function (album) {
        album = JSON.parse(album);

        if (album.id in albumMap) {
            // update album if necessary
            updateAlbum(album)
        } else {
            // album is new, create the new element and mapp it
            var album_div = createAlbumDiv(album)
            // console.log(`created new album div ${album_div}`)
            albumMap[album.id] = album_div;
            $('#albums-container').append(album_div);
        }
        // Append div to container
    });
}

function updateAlbum(album) {
    // Update existing element if content differs
    var existingElement = albumMap[album.id];
    // var existingContent = existingElement;
    var existingContent = existingElement.html();
    var newContent = createAlbumContent(album);
    // console.log(`existingContent: ${existingContent}`)
    // console.log(`newContent:      ${newContent}`)
    if (existingContent !== newContent) {
        console.log(`replacing content with: ${newContent}`)
        existingElement.html(newContent);
    }
}

function createAlbumDiv(album) {
    // Create a new div element
    var div = $(`<div class="album" id="${album.id}"></div>`);
    div.html(createAlbumContent(album));
    return div
}

function createAlbumContent(album) {
    // DONE add button to remove album from history
    // TODO add button to remove album completely (db and files)
    // TODO add tracks
    // TODO add download button

    // extra div outside the card div because it will be removed by the .html() function
    // using .html() to serialize the data the same way as it will be loaded in updateAlbum() for confrontation
    var html = $(`<div>
    <div id="${album.id}_content">
        <div class="card border-dark mb-3">
            <div class="row g-0">
                <div class="col">
                    <div class="card-body">
                        <img src="data:image/jpeg;base64,${album.thumbnail}" class="img-fluid rounded">
                    </div>
                </div>
                <div class="col-md-10">
                    <div class="card-body">
                        <h5 class="card-title">${album.title}</h5>
                        <p class="card-text">${album.status}</p>
                        <p class="card-text">${album.download_percentage}</p>
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-primary disabled text-nowrap">Download album</button>
                            <a class="btn btn-primary disabled" role="button" href="download/${album.id}" target="_blank">
                                <!-- mdi:theme -->
                                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M13 5v6h1.17L12 13.17L9.83 11H11V5zm2-2H9v6H5l7 7l7-7h-4zm4 15H5v2h14z"/></svg>
                            </a>
                        </div>   
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-danger disabled text-nowrap">Delete</button>
                            <button class="btn btn-danger" role="button" onClick="deleteAlbum('${album.id}');">
                                <!-- mdi:theme -->
                                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M7 21q-.825 0-1.412-.587T5 19V6H4V4h5V3h6v1h5v2h-1v13q0 .825-.587 1.413T17 21zM17 6H7v13h10zM9 17h2V8H9zm4 0h2V8h-2zM7 6v13z"/></svg>
                            </button>
                        </div>                        
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-secondary disabled text-nowrap">Album URL</button>
                            <a class="btn btn-secondary" role="button" href="${album.url}" target="_blank">
                                <!-- mdi:theme -->
                                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M14 3v2h3.59l-9.83 9.83l1.41 1.41L19 6.41V10h2V3m-2 16H5V5h7V3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7h-2z"/></svg>                            
                            </a>
                        </div>
                        <div id="${album.id}_tracks">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    </div>
    `).html()
    return html
}

// function createTracksList(album){
//     var html = $(`<div>
//     <ul id="${album.id}_tracks" class="list-group">
//     </ul>   
//     </div>
//     `).html()
//     return html 
// }

// function createTrackListItem(track){
//     html = $(`
//     <li id="5f4f9440773948afa159e557bcc3233d" class="list-group-item">
//         01 Crystal Pier 
//         <span class="badge text-bg-success">mp3</span>
//         <div class="btn-group" role="group">
//             <button type="button" class="btn btn-primary disabled text-nowrap">Download</button>
//             <a class="btn btn-primary" role="button" href="downloads\\\\Dorfromantik Soundtrack Vol. 2\\\\flac\\\\01 Crystal Pier.flac" target="_blank">
//                 <!-- mdi:theme -->
//                 <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M13 5v6h1.17L12 13.17L9.83 11H11V5zm2-2H9v6H5l7 7l7-7h-4zm4 15H5v2h14z"/></svg>
//             </a>
//         </div>                                
//         <div class="btn-group" role="group">
//             <button type="button" class="btn btn-secondary disabled text-nowrap">Track URL</button>
//             <a class="btn btn-secondary" role="button" href="https://epsilon.vgmsite.com/soundtracks/dorfromantik-soundtrack-vol.-2-2022/yyduovwddt/01%20Crystal%20Pier.flac" target="_blank">
//                 <!-- mdi:theme -->
//                 <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M14 3v2h3.59l-9.83 9.83l1.41 1.41L19 6.41V10h2V3m-2 16H5V5h7V3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7h-2z"/></svg>                            
//             </a>
//         </div>                                
//     </li>
//     `)
//     return html
// }

function fetchTracks(album){
    $.ajax({
        url: `/album/${album.id}/tracks`,
        type: 'GET',
        success: function (data) {
            t = createTracksTable()
            rows = ''
            data.forEach(function (track) {
                track = JSON.parse(track);
                rows += createTrackTableRow(track)
                if (album.id in albumMap) {
                    // update album if necessary
                    updateAlbum(album)
                } else {
                    // album is new, create the new element and mapp it
                    var album_div = createAlbumDiv(album)
                    // console.log(`created new album div ${album_div}`)
                    albumMap[album.id] = album_div;
                    $('#albums-container').append(album_div);
                }
                // Append tracks to container
                [TRACKS]
                t.replace("[TRACK_ROWS]", rows)
            });
        },
        error: function (xhr, status, error) {
            // Handle errors here
            console.error(xhr.responseText);
        }
    });
}

function createTracksTable(){
    t = `<table class="table">
        <thead>
            <tr>
                <th scope="col">Title</th>
                <th scope="col">Actions</th>
                <th scope="col">Size</th>
                <th scope="col">Status</th>
            </tr>
        </thead>
        <tbody class="table-group-divider">
            [TRACK_ROWS]
        </tbody>
    </table>`
    return t
}

function createTrackTableRow(track){
    tr = `
    <tr>
        ${ _renderTrackTitle(track) }
        ${ _renderTrackActions(track) }
        <td>${track.filesize}</td>
        <td>${track.status}</td>
    </tr>
    `
    return tr;
}

function _renderTrackTitle(track){
    let split_track_name = track.name.split('.')
    let track_ext = split_track_name.pop()
    let track_name = split_track_name.join('.')    
    title = `<td>${track_name} <span class="badge text-bg-success">${track_ext}</span></td>`
    return title
}

function _renderTrackActions(track){
    // TODO actually use track data
    actions = `
        <td>
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-primary disabled text-nowrap">Download</button>
                <a class="btn btn-primary" role="button" href="downloads\\\\Dorfromantik Soundtrack Vol. 2\\\\flac\\\\01 Crystal Pier.flac" target="_blank">
                    <!-- mdi:theme -->
                    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M13 5v6h1.17L12 13.17L9.83 11H11V5zm2-2H9v6H5l7 7l7-7h-4zm4 15H5v2h14z"/></svg>
                </a>
            </div>                                
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-secondary disabled text-nowrap">Track URL</button>
                <a class="btn btn-secondary" role="button" href="https://epsilon.vgmsite.com/soundtracks/dorfromantik-soundtrack-vol.-2-2022/yyduovwddt/01%20Crystal%20Pier.flac" target="_blank">
                    <!-- mdi:theme -->
                    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M14 3v2h3.59l-9.83 9.83l1.41 1.41L19 6.41V10h2V3m-2 16H5V5h7V3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7h-2z"/></svg>                            
                </a>
            </div>               
        </td>
    `
    return actions
}

function fetchTracks() {
    $.ajax({
        url: '/tracks',  // Your Flask route for fetching tracks
        type: 'GET',
        success: function (data) {
            // Handle the response here
            console.log(data);
        },
        error: function (xhr, status, error) {
            // Handle errors here
            console.error(xhr.responseText);
        }
    });
}

function deleteAlbum(id) {
    console.log('sending delete request for album '+id)
    $.ajax({
        url: '/album/' + id,
        type: 'DELETE',
        success: function(result) {
            let album_container ='#' +id + '_content'
            $(album_container).remove();
        },
        error: function (xhr, status, error) {
            console.error(xhr.responseText);
        }
    });    
}


// Wait for the DOM to be ready
$(document).ready(function () {
    // Add a submit event listener to the form
    $('#playlistForm').submit(function (event) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // Serialize the form data
        const formData = $(this).serialize();

        // Send the form data via AJAX to the 'processurl' endpoint
        $.post('/processurl', formData)
            .done(function (response) {
                // Handle successful response
                console.log('Form data sent successfully');
            })
            .fail(function (xhr, status, error) {
                // Handle errors
                console.error('Error sending form data:', error);
            });
    });


});


$(document).ready(function () {
    // Call fetchAlbums every second
    setInterval(fetchAlbums, 1000); // 1000 milliseconds = 1 second    
    // Call fetchTracks every second
    // setInterval(fetchTracks, 1000); // 1000 milliseconds = 1 second         
});