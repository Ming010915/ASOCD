var currentUser = document.getElementById('userSelection').value;
var displayedImages = [];
var noMorePic = false;
var imageCount = 0;
var imageList = [];
var currentQuestion = 1;
var userScore = 0;
var currentImageList = [];
var currentImageNumber = -1;
var totalImageNumber = 0;

fetch('/current_user', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'username=' + encodeURIComponent(currentUser),
})

fetch('/get_used_images')
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        displayedImages = data;
    })
    .catch(function (error) {
        console.error('Error:', error);
    });

fetch('/number_of_images')
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        imageCount = data.length;
        imageList = data.image_files;
    })
    .catch(function (error) {
        console.error('Error:', error);
    });

function changeUser() {
    if (currentImageNumber == -1) {
        document.getElementById('previousImage').disabled = true;
    } else {
        document.getElementById('previousImage').disabled = false;
    }
    currentUser = document.getElementById('userSelection').value;

    fetch('/current_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'username=' + encodeURIComponent(currentUser),
    })

    fetch('/get_used_images')
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            displayedImages = data;
            if (displayedImages.length == imageCount) {
                noMorePic = true;
                disableButtons();
                changeImage();
            } else {
                noMorePic = false;
                enableButtons();
                changeImage();
            }
        })
        .catch(function (error) {
            console.error('Error:', error);
        });
}

function getImageTag() {
    if (currentImageNumber+1 == totalImageNumber) {
        if (displayedImages.length == imageCount) {
            currentImageNumber = currentImageNumber + 1;
            noMorePic = true;
            return '<p id="no-more-images">No more images to show</p>';
        }
        var randomImage;
        do {
            randomImage = imageList[Math.floor(Math.random() * imageCount)];
            var imageNameWithoutExtension = randomImage.replace(/\.[^/.]+$/, "");
        } while (displayedImages.includes(imageNameWithoutExtension));

        displayedImages.push(imageNameWithoutExtension);
        currentImageList.push(imageNameWithoutExtension);
        totalImageNumber++;
        currentImageNumber++;   

        var testImage = new Image();
        testImage.src = 'static/images/' + randomImage;

        if (testImage.width > 0) {
            return '<img src="' + testImage.src + '"/>';
        } else {
            return '<img src="' + testImage.src + '" alt="Oh no, the image is broken!"/>';
        }
    } else {
        currentImageNumber = currentImageNumber + 1;
        return '<img src="static/images/' + currentImageList[currentImageNumber] + '.png"/>';
    }
}

function changeImage() {
    var imageContainer = document.getElementById('image-container');
    imageContainer.innerHTML = getImageTag();
    document.getElementById('myCheckbox').checked = false;
    enableButtons();
    currentQuestion = 1;
    changeLabel();

    if (noMorePic) {
        disableButtons();
        document.getElementById('nextImage').disabled = true;
        document.getElementById('question').innerText = " ";
    }

    fetch('/delete_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'username=' + encodeURIComponent(currentUser) + '&imageName=' + encodeURIComponent(document.getElementById('image-container').firstChild.src),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    
}

function previousImage() {
    if (currentImageNumber > 0) {
        fetch('/delete_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'username=' + encodeURIComponent(currentUser) + '&imageName=' + encodeURIComponent(document.getElementById('image-container').firstChild.src),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        currentQuestion = 1;
        currentImageNumber--;
        document.getElementById('image-container').innerHTML = '<img src="static/images/' + currentImageList[currentImageNumber] + '.png"/>';
        enableButtons();
        noMorePic = false;

        fetch('/delete_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'username=' + encodeURIComponent(currentUser) + '&imageName=' + encodeURIComponent(document.getElementById('image-container').firstChild.src),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
}

function changeQuestion(data) {
    if (currentQuestion == 1) {
        if (data == 1) {
            currentQuestion = 4;
        } else if (data == 5) {
            currentQuestion = 2;
        } else if (data == 7) {
            currentQuestion = 6;
            recordFeedback(0);
        }
        document.getElementById("impossible").style.display = 'none';

    } else if (currentQuestion == 2) {
        if (data == 1) {
            currentQuestion = 4;
        } else if (data == 5) {
            currentQuestion = 3;
        }
    } else if (currentQuestion == 3) {
        if (data == 1) {
            currentQuestion = 4;
        } else if (data == 5) {
            currentQuestion = 6;
            recordFeedback(0);
        }
    } else if (currentQuestion == 4) {
        if (data == 1) {
            currentQuestion = 6;
            recordFeedback(0);
        } else if (data == 5) {
            currentQuestion = 5;
        }
    } else if (currentQuestion == 5) {
        currentQuestion = 6;
        recordFeedback(0);
    }
    changeLabel();
}

function changeLabel() {
    if (currentQuestion == 1) {
        document.getElementById('question').innerText = "Is there a reasonable circle and are the 12 numbers well distributed within the circle?";
        document.getElementById("impossible").style.display = 'inline';
    } else if (currentQuestion == 2) {
        document.getElementById('question').innerText = "Are all 12 numbers included?";
    } else if (currentQuestion == 3) {
        document.getElementById('question').innerText = "Was there a reasonable circle?";
    } else if (currentQuestion == 4) {
        document.getElementById('question').innerText = "Are both hands well drawn?";
    } else if (currentQuestion == 5) {
        document.getElementById('question').innerText = "Are both hands placed on the correct numbers but the lengths are interchanged?";
    } else if (currentQuestion == 6) {
        document.getElementById('question').innerText = "END OF TEST";
        disableButtons();
        document.getElementById('previousImage').disabled = true;
        document.getElementById('image-container').innerHTML = '';
    }
}

function disableButtons() {
    document.getElementById('yes').disabled = true;
    document.getElementById('no').disabled = true;
    document.getElementById('impossible').disabled = true;
    document.getElementById('comments').disabled = true;
    document.getElementById('myCheckbox').disabled = true;
}

function enableButtons() {
    var buttons = document.querySelectorAll('.button-container button');
    document.getElementById('comments').disabled = false;
    document.getElementById('myCheckbox').disabled = false;
    buttons.forEach(function (button) {
        button.disabled = false;
    });
    if (currentImageNumber == 0) {
        document.getElementById('previousImage').disabled = true;
    } else {
        document.getElementById('previousImage').disabled = false;
    }
}

window.addEventListener('load', function () {
    changeImage();
});

function recordFeedback(feedbackValue) {
    var comments = document.getElementById('comments').value;
    var imageName = document.getElementById('image-container').firstChild.src;
    var isCheckboxChecked = document.getElementById('myCheckbox').checked;

    fetch('/record_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'username=' + encodeURIComponent(currentUser) + '&score=' + encodeURIComponent(feedbackValue) + '&comments=' + encodeURIComponent(comments) + '&imageName=' + encodeURIComponent(imageName) + "&hard=" + encodeURIComponent(isCheckboxChecked) + "&question=" + encodeURIComponent(currentQuestion)
    })
        .then(response => response.text())
        .then(userScore = userScore + feedbackValue)
        .then(data => {
            changeQuestion(feedbackValue);
            document.getElementById('comments').value = '';
        })
        .catch(error => {
            console.error('Error:', error);
        });
}