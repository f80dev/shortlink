

let domain="http://17cf9cm6g5cdr3s3o04cqvjvus.ingress.europlots.com/"

function sendUrlToServer(url) {
  return new Promise((resolve, reject) => {
    {
      let requestOptions = {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url: url})
      }

      fetch(domain+"api/add", requestOptions).then(
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



document.getElementById('myButton').addEventListener('click', function() {
  chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
    // Access the active tab and do something based on the button click
    let rep = await sendUrlToServer(tabs[0].url);
    document.getElementById("result").innerText=domain+rep
  });
});
