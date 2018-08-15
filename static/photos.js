/**
 * Module containing helper functions for initialization of photo grid pages.
 */

/**
 * Parse picture index and gallery index from URL (#&pid=1&gid=2)
 * This function was copied from the photoswipe documentation.
 */
function photoswipeParseHash() {
    var hash = window.location.hash.substring(1),
    params = {};

    if (hash.length < 5) {
        return params;
    }

    var vars = hash.split('&');
    for (var i = 0; i < vars.length; i++) {
        if (!vars[i]) {
            continue;
        }
        var pair = vars[i].split('=');
        if (pair.length < 2) {
            continue;
        }
        // pair[0] == "gid" or "pid"
        // pair[1] == the value for "gid" or "pid"
        params[pair[0]] = pair[1];
    }
    if (params.gid) {
        params.gid = parseInt(params.gid, 10);
    }

    return params;
};


/**
 * Get the numeric index of the photo with the given pid. pid is usually the
 * filename of the image.
 */
function getIndexOfPid(pswpItems, pid) {
    var index = 0;
    for (var j = 0; j < pswpItems.length; j++) {
        if (pswpItems[j].pid == pid) {
            index = j;
            break;
        }
    }
    return index;
}


/**
 * Makes a REST call to get the JSON object containing lightbox and grid
 * info for the given URL.
 */
function getPathContents(url) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", url, false);
    xhttp.send();
    return JSON.parse(xhttp.responseText);
}


/**
 * Generate breadcrumb links for a path by splitting it on forward slashes.\
 * Puts the breadcrumbs in the supplied UL element.
 */
function setBreadcrumbs(url, ulElement) {
    var accumUrl = "";
    // Bit of a hack to handle the single-slash URL
    var aCrumbs;
    if (url == "/") {
        aCrumbs = [""];
    } else {
        var aCrumbs = url.split("/");
    }
    for (var i = 0; i < aCrumbs.length; i++) {
        var crumb = aCrumbs[i];
        console.log("crumb = " + crumb);
        var crumbText;
        if (crumb == "") {
            crumbText = "Photos";
            accumUrl += "/photos";
        } else {
            crumbText = crumb;
            accumUrl += "/" + crumbText;
        }
        console.log("crumbText = " + crumbText);
        console.log("accumUrl = " + accumUrl);
        li = document.createElement("li");
        link = document.createElement("a");
        link.href = accumUrl;
        link.innerText = crumbText;
        li.appendChild(link);
        ulElement.appendChild(li);
    }
}
