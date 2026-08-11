const checks = [
  'Bring a printed copy (color preferred) of expiring passport\'s data page',
  'Photocopy of Social Security card',
  'For minors, bring a printed copy (color preferred) of each parent\'s passport data page and Social Security card',
  'Copy of your Shekou police registration document (contains your Chinese address)',
  'Passport photos (will be stapled to your application at Desk 1)',
  'Shipment / mailing label for passport return delivery',
  'Decide before: keep expiring passport to mail later via EMS, or leave it at the consulate?',
];
const cl = document.getElementById('checklist');
if (cl) {
  checks.forEach((text, i) => {
    const div = document.createElement('div');
    div.className = 'flex gap-3 items-start p-2 hover:bg-gray-50 rounded-lg';
    div.innerHTML = `<input type="checkbox" id="c${i+1}" class="mt-0.5 h-4 w-4 accent-brand flex-shrink-0">
      <label for="c${i+1}" class="text-sm cursor-pointer">${text}</label>`;
    cl.appendChild(div);
  });
}

const miniApps = [
  { name: 'Meituan', desc: 'Food & grocery delivery to your door', icon: 'assets/icons/meituan.jpg' },
  { name: 'Distinct Healthcare 卓正医疗', desc: 'Concierge healthcare service and local clinic accepted by company insurance', icon: 'assets/icons/distincthealthcare.png' },
  { name: '京东 JD (Shopping; Jīng Dōng)', desc: "It's the biggest online retail platform. English interface available in JD Mini Program in WeChat.", icon: 'assets/icons/jd.jpg' },
  { name: 'GBA Ferries 粤港快船', desc: 'Ferry tickets to Hong Kong or Macau', icon: 'assets/icons/gbaferries.jpg' },
  { name: 'One 蛇口-招商邮轮 (One Shekou Port, CM Cruise)', desc: 'Ferry ticket booking, schedules, and pricing for the Shekou cruise terminal', icon: 'assets/icons/oneshekoucruise.png' },
  { name: 'SIS Connect', desc: 'For families with kids at Shekou International School', icon: 'assets/icons/sisconnect.jpg' },
  { name: 'Epermarket South', desc: 'Cloud supermarket with foreign goods and prepared foods', icon: 'assets/icons/epermarket.png' },
  { name: 'Chaotao Shop', desc: 'Uniform shop for Shekou International School', icon: 'assets/icons/chaotao.jpg' },
  { name: '乘车码 (Chéng Chē Mǎ)', desc: 'Pay subway & bus fares in Shenzhen (works in other cities too)', icon: 'assets/icons/chengchema.jpg' },
  { name: 'Silver Palate Groceries', desc: 'Western grocery items you can\'t find at Ole', icon: 'assets/icons/silverpalate.jpg' },
];
const mag = document.getElementById('mini-apps-grid');
if (mag) {
  miniApps.forEach(a => {
    const d = document.createElement('div');
    d.className = 'flex gap-3 p-3 bg-gray-50 rounded-lg items-start';
    const iconHtml = a.icon
      ? `<img src="${a.icon}" alt="" class="flex-shrink-0 w-8 h-8 rounded-lg object-cover border border-gray-200" loading="eager">`
      : `<div class="flex-shrink-0 w-8 h-8 bg-brand-lt rounded-lg flex items-center justify-center">
        <svg class="icon w-4 h-4 text-brand" aria-hidden="true"><use href="#ic-app"/></svg></div>`;
    d.innerHTML = `${iconHtml}
      <div><p class="font-medium">${a.name}</p><p class="text-xs text-gray-500 mt-0.5">${a.desc}</p></div>`;
    mag.appendChild(d);
  });
}

const apps = [
  { name: "Sam's Club (China)", desc: 'The company will provide a free membership to Sam\'s Club. It does not use the US app. See App Store notes below.', icon: 'assets/icons/samsclub.jpg', url: 'https://apps.apple.com/us/app/id818237113' },
  { name: 'Alipay', desc: 'Your backup payment method alongside WeChat. Link at least two credit/debit cards so you have a working fallback if one gets blocked.', icon: 'assets/icons/alipay.jpg', url: 'https://apps.apple.com/us/app/alipay/id333206289' },
  { name: 'AMap (Maps)', desc: 'Think Google Maps. Apple Maps works, but your location is purposely not accurate.', icon: 'assets/icons/amap.jpg', url: 'https://apps.apple.com/us/app/id461703208' },
  { name: 'Didi (Ride Sharing)', desc: "Think Uber or Lyft. An English interface appears after signing in. Drivers typically read off the last 4 digits of your phone number to confirm you're their rider.", icon: 'assets/icons/didi.jpg', url: 'https://apps.apple.com/us/app/id554499054' },
  { name: 'GlobalSolutions', desc: 'Health insurance management.', icon: 'assets/icons/globalsolutions.jpg', url: 'https://apps.apple.com/us/app/id500753535' },
  { name: 'Railway 12306 (Train Tickets)', desc: 'Book high-speed train travel across China.', icon: 'assets/icons/railway12306.jpg', url: 'https://apps.apple.com/us/app/id564818797' },
  { name: '深圳地铁 (Subway Tickets; Shēn Zhèn Dì Tiě)', desc: 'Install and setup this app for the QR code the Shenzhen Metro will need for entry and exit.', icon: 'assets/icons/shenzhenmetro.jpg', url: 'https://apps.apple.com/us/app/id848926994' },
  { name: 'Trip.com (Travel Booking, eSIM)', desc: 'International eSIM plans (auto-renewing) bypass the Great Firewall. Download before you arrive. You may also use a VPN to purchase eSIMs.', icon: 'assets/icons/tripcom.jpg', url: 'https://apps.apple.com/us/app/id681752345' },
  { name: 'BNESIM', desc: 'International eSIM plans with data that lasts as long as you have the eSIM, and you can add other countries to the same eSIM. Download before you arrive. You may also use a VPN to purchase eSIMs.', icon: 'assets/icons/bnesim.jpg', url: 'https://apps.apple.com/us/app/id1598924185' },
  { name: 'QWeather', desc: 'The interface includes radar and an approximate timeline for rain.', icon: 'assets/icons/qweather.jpg', url: 'https://apps.apple.com/us/app/id1461458147' },
];
const ag = document.getElementById('apps-grid');
if (ag) {
  apps.forEach(a => {
    const d = document.createElement(a.url ? 'a' : 'div');
    d.className = 'app-card flex gap-3 p-3 border border-gray-100 bg-gray-50 rounded-lg items-start' + (a.url ? ' hover:bg-gray-100 transition' : '');
    if (a.url) { d.href = a.url; d.target = '_blank'; d.rel = 'noopener'; }
    const badge = a.badge ? `<span style="font-size:10px;font-weight:700;background:#c2410c;color:#1e293b;border-radius:9999px;padding:1px 8px;margin-left:6px;vertical-align:middle;">${a.badge}</span>` : '';
    const iconHtml = a.icon
      ? `<img src="${a.icon}" alt="" class="flex-shrink-0 w-8 h-8 rounded-lg object-cover border border-gray-200" loading="eager">`
      : `<div class="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center">
        <svg class="icon w-4 h-4 text-gray-500" aria-hidden="true"><use href="#ic-phone"/></svg></div>`;
    d.innerHTML = `${iconHtml}
      <div><p class="font-medium">${a.name}${badge}</p><p class="text-xs text-gray-500 mt-0.5">${a.desc}</p></div>`;
    ag.appendChild(d);
  });
}

function toggleHkgGuide() {
  const el    = document.getElementById('hkg-embed');
  const lbl   = document.getElementById('hkg-btn-label');
  const chv   = document.getElementById('hkg-chevron');
  const card  = document.getElementById('hkg-toggle-card');
  const open = el.style.display === 'none' || el.style.display === '';
  el.style.display  = open ? 'block' : 'none';
  lbl.textContent   = open ? 'Hide full guide' : 'Show full step-by-step guide';
  chv.style.transform = open ? 'rotate(180deg)' : '';
  card.style.borderBottomLeftRadius  = open ? '0' : '';
  card.style.borderBottomRightRadius = open ? '0' : '';
  card.style.marginBottom = open ? '0' : '';
  if (open) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function toggleArrivalCard() {
  const el    = document.getElementById('arrival-embed');
  const lbl   = document.getElementById('arrival-btn-label');
  const chv   = document.getElementById('arrival-chevron');
  const card  = document.getElementById('arrival-toggle-card');
  const open = el.style.display === 'none' || el.style.display === '';
  el.style.display  = open ? 'block' : 'none';
  lbl.textContent   = open ? 'Hide step-by-step guide' : 'Show step-by-step guide';
  chv.style.transform = open ? 'rotate(180deg)' : '';
  card.style.borderBottomLeftRadius  = open ? '0' : '';
  card.style.borderBottomRightRadius = open ? '0' : '';
  card.style.marginBottom = open ? '0' : '';
  if (open) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

(function () {
  const tempEl = document.getElementById('wx-temp');
  const tempUnitEl = document.getElementById('wx-temp-unit');
  const humEl = document.getElementById('wx-humidity');
  const humUnitEl = document.getElementById('wx-humidity-unit');
  const comfortEl = document.getElementById('wx-comfort');
  const dewEl = document.getElementById('wx-dewpoint');
  const updatedEl = document.getElementById('wx-updated');
  if (!tempEl) return;

  function comfortLevel(dewC) {
    if (dewC < 12.8) return 'Dry';
    if (dewC < 15.6) return 'Comfortable';
    if (dewC < 18.3) return 'Humid';
    if (dewC < 21.1) return 'Muggy';
    if (dewC < 23.9) return 'Oppressive';
    return 'Miserable';
  }

  fetch('https://api.open-meteo.com/v1/forecast?latitude=22.4808&longitude=113.9077&current=temperature_2m,relative_humidity_2m,dew_point_2m&timezone=Asia%2FShanghai')
    .then(r => r.json())
    .then(data => {
      const c = data.current;
      tempEl.textContent = Math.round(c.temperature_2m);
      tempUnitEl.textContent = '°C';
      humEl.textContent = Math.round(c.relative_humidity_2m);
      humUnitEl.textContent = '%';
      comfortEl.textContent = comfortLevel(c.dew_point_2m);
      dewEl.innerHTML = Math.round(c.dew_point_2m) + '°<sup style="font-size:0.6em;">C</sup>';
      const time = new Date(c.time);
      updatedEl.textContent = 'Live conditions for Shekou, Nanshan, Shenzhen, PRC – updated ' + time.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) + '.';
    })
    .catch(() => {
      tempEl.textContent = '–';
      humEl.textContent = '–';
      comfortEl.textContent = 'Unavailable';
      updatedEl.textContent = 'Could not load live weather data.';
    });
})();
