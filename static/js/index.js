// Mapping between album IDs and corresponding HTML elements
var albumMap = {};

function fetchAlbums() {
    $.ajax({
        url: '/albums',  // Your Flask route for fetching albums
        type: 'GET',
        success: function (data) {
            // Handle the response here
            // console.log(data);
            // Parse JSON response
            // var albums = JSON.parse(data);
            // Invoke callback function with parsed album data
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
    var existingContent = existingElement;
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
    // TODO add button to remove album from history
    // TODO add button to remove album completely (db and files)
    // TODO add tracks
    // TODO add download button

    // extra div outside the card div because it will be removed by the .html() function
    // using .html() to serialize the data the same way as it will be loaded in updateAlbum() for confrontation
    var html = $(`<div>
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
                    <a href="${album.url}" target="_blank" class="btn btn-link">${album.url}</a>
                </div>
            </div>
        </div>
    </div>
    </div>
    `).html()
    return html
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