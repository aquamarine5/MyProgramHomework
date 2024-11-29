/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
 * v3, 2024/11/29.
 */
let a = document.getElementsByTagName("progress"); for (let b of a) { b.value = b.max; } let c = document.getElementsByClassName("_indicator_mumtr_18"); for (let d of c) { d.textContent = d.textContent.replace(/(\d+)\/(\d+)/g, '$2/$2'); }; let k = document.getElementsByTagName("svg"); for (let i of k) { if (i.innerHTML == '<circle cx="12" cy="12" r="12" fill="#575BFD"></circle><path d="M16.5 11.134C17.1667 11.5189 17.1667 12.4811 16.5 12.866L10.5 16.3301C9.83333 16.715 9 16.2339 9 15.4641L9 8.5359C9 7.7661 9.83333 7.28497 10.5 7.66987L16.5 11.134Z" fill="white"></path>') { i.innerHTML = '<circle cx="12" cy="12" r="12" fill="#40BF9C"></circle><path d="M7.625 12.625L10.125 15.125L16.375 8.875" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>' } }