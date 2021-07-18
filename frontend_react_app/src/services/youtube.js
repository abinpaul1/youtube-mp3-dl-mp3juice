import jsonp from 'simple-jsonp-promise'

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
    const url = 'api/youtube-dl/search'
    const data = { search : queryString }
    // post request to flask server
    return fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    .then(response => response.json());
}


export const downloadAudioInNewWindow = (youtubeId) => {
  const encodedYoutubeId = encodeURIComponent(youtubeId);
  const download_url = `api/youtube-dl/download?ybid=${encodedYoutubeId}`
  // Open a new window with the url
  window.open(download_url);
}