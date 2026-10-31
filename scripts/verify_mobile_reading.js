async page => {
  await page.route('https://**',route=>route.abort());
  const results=[];
  for (const width of [360,390,430]) {
    await page.setViewportSize({width,height:844});
    for (const file of ['book1.html','index.html','agent-bible.html','claude-code-bible.html','practical-bible.html']) {
      await page.goto('http://127.0.0.1:8937/'+file,{waitUntil:'domcontentloaded'});
      await page.waitForTimeout(180);
      const initial=await page.evaluate(()=>({path:location.pathname,width:innerWidth,body:document.body.scrollWidth,
        fixed:[...document.querySelectorAll('body *')].filter(e=>getComputedStyle(e).position==='fixed'&&e.getBoundingClientRect().height>0).slice(0,15).map(e=>({id:e.id,tag:e.tagName,top:Math.round(e.getBoundingClientRect().top),height:Math.round(e.getBoundingClientRect().height)})),
        buttons:[...document.querySelectorAll('button')].filter(e=>!!(e.offsetWidth||e.offsetHeight)).slice(0,12).map(e=>({id:e.id,text:e.textContent.trim().slice(0,40)}))}));
      if(width===390)await page.screenshot({path:'C:/Users/user/AppData/Local/Temp/bible-mobile-'+file+'.png'});
      const route=page.locator('#aib-learning-route');
      await route.getByText('준비물과 읽는 순서',{exact:true}).click({timeout:3000});
      if(!await route.getByText(/권 번호는 주제 구분/).isVisible())throw Error('Reading prerequisites did not open: '+file);
      if(initial.body>width+1)throw Error('Body overflow: '+file);
      if(await page.locator('#completion-overlay.is-open').count())throw Error('Reading interrupted by completion modal: '+file);
      let toc='not applicable';
      const tocSelector=file==='agent-bible.html'?'#mobile-toc-btn':file==='claude-code-bible.html'?'#sidebar-toggle':file==='index.html'?'#mob-toc-btn':file==='practical-bible.html'?'.menu-toggle':null;
      if(tocSelector){
        const control=page.locator(tocSelector);
        const box=await control.boundingBox();
        if(!box||box.width<44||box.height<44)throw Error('Small TOC target: '+file);
        await control.click({timeout:3000});
        if(!await page.locator('#sidebar').evaluate(e=>e.classList.contains('mobile-open')||e.classList.contains('open')))throw Error('TOC failed to open: '+file);
        if(file==='agent-bible.html')await page.locator('#mobile-overlay').click({position:{x:width-10,y:100},timeout:3000});
        else if(file==='index.html')await page.locator('#toc-overlay').click({position:{x:width-10,y:100},timeout:3000});
        else if(file==='practical-bible.html')await page.locator('.mobile-toc-close').click({timeout:3000});
        else await control.click({timeout:3000});
        if(await page.locator('#sidebar').evaluate(e=>e.classList.contains('mobile-open')||e.classList.contains('open')))throw Error('TOC failed to close: '+file);
        toc='PASS';
      }
      if(await page.locator('#aib-update-20261025').isVisible())await page.locator('#aib-update-20261025').scrollIntoViewIfNeeded();
      const locked=await page.locator('#aib-practice-20261031').isVisible();
      if(locked)throw Error('Paid exercise exposed: '+file);
      results.push({...initial,prerequisites:'PASS',paidExerciseHidden:!locked,toc});
    }
  }
  return results;
}
