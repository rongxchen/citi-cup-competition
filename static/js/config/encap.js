var baseHost = "http://172.28.157.119:8000";

function myAxios(method, url, data=null) {
    return axios({
        method: method,
        url: baseHost + url,
        data: data
    }).then((res) => {
        return res;
    })
}

function myXhr(method, url, data=null) {
    var xhr = new XMLHttpRequest();
    var adjUrl = baseHost + url;
    xhr.open(method, adjUrl, false);
    xhr.send();
    return xhr;
}