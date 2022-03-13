"use strict";
window.addEventListener("DOMContentLoaded", async function getAccessTime(){
    let newH2 = document.createElement("h2");
    let accessTime = await eel.get_access_time()();
    let accessTimeText = document.createTextNode(accessTime["access_year"]+"年"+accessTime["access_month"]+"月"+accessTime["access_date"]+"日"+accessTime["access_hour"]+"時"+accessTime["access_minute"]+"分のネットワーク図");
    newH2.appendChild(accessTimeText);
    let graphDiv = document.getElementById("graph");
    graphDiv.parentNode.insertBefore(newH2, graphDiv);
    })