import jsonp from 'simple-jsonp-promise'

const API_PATH = 'api'

export const suggest = (term) => {
    const url = 'https://clients1.google.com/complete/search'
    const params = {
      client: "youtube",
      hl: "en",
      ds: "yt",
      q: term,
    }
    return jsonp(url, {data: params}).then((res) => {
      return res[1].map((item) => item[0]);
    })
}

// Fetch details of search from flask server 
export const youtubeSearch = (queryString) => {
    const url = `${API_PATH}/youtube-dl/search`
    const data = { search : queryString }
    // post request to flask server
    return fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    .then(response => response.json());
}

// Sends convert request to server and return true on success,
// false on failure
export const triggerVideoConversion = async (youtubeId) => {
    const url = `${API_PATH}/youtube-dl/convert`
    const data = { ybid : youtubeId }
    // post request to flask server
    return fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    .then(response => response.status === 200)
    .catch(error => false);
}


export const downloadAudioInNewWindow = (youtubeId) => {
  const encodedYoutubeId = encodeURIComponent(youtubeId);
  const download_url = `${API_PATH}/youtube-dl/download?ybid=${encodedYoutubeId}`
  // Open a new window with the url
  window.open(download_url);
}