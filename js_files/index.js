// {'ga': ['!function(f,b,e,v,n,t,s) ...', ['G123456','G13244']], 'kakao': ['!function(f,b,e,v,n,t,s) ...', ['G123456','G13244']], ...}
import {mediums} from './mediums';
// {'event1': ['button1.addEventListener("click", (ev)=> ...)', "/^https?:\\/\\/(?:www\\.)?[-a-zA-Z ..."], ...}
import {events} from './events';
// {'tag1': t=>{gtag("event","submit")}, 'tag2': t=>{gtag("event","submit")}}
import {tags} from './tags';

console.log(mediums)
console.log(events)
console.log(tags)
