
// Facebook Share function
function fbShare(){
    let postUrl = encodeURI(document.location.href);
    window.open(`https://www.facebook.com/sharer.php?u=${postUrl}`);
};

