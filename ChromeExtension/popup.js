

//let domain="https://x.f80.fr/"
//let domain="http://s.f80.fr/"
let domain="https://t.f80.fr/"
//let domain="https://192.168.1.62/"
//let domain="https://provider.rayjin.tech:30120/"

function sendUrlToServer(url) {
  return new Promise((resolve, reject) => {
    {
      let requestOptions = {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url: url})
      }

      fetch(domain+"api/add/", requestOptions).then(
        response => {
          if (!response.ok) {
            reject(new Error(`Error sending data: ${response.statusText}`))
          }
          resolve(response.text()); // Handle response accordingly
        }
      )
    }
  })
}


//liste des événements
document.getElementById('btnCopy').addEventListener('click', function() {
  navigator.clipboard.writeText(document.getElementById("result").innerText)
  document.getElementById('btnCopy').style.visibility="hidden"
});

document.getElementById('btnShare').addEventListener('click', function() {
  navigator.share({url:document.getElementById("result").innerText})
});

document.addEventListener('DOMContentLoaded', function() {
  setTimeout(()=>{
    chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
      // Access the active tab and do something based on the button click
      let rep = await sendUrlToServer(tabs[0].url);
      document.getElementById("result").innerText=domain+rep
      document.getElementById("result_link").href=domain+rep
    });
  },100)
});
