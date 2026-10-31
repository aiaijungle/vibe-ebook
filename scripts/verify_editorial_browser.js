async page => {
  const results = [];
  for (const width of [390,1280]) {
    for (const file of ['book1.html','index.html','agent-bible.html','claude-code-bible.html','practical-bible.html','start-here.html']) {
      await page.setViewportSize({width,height:844});
      await page.goto('http://127.0.0.1:8937/'+file);
      const result=await page.evaluate(()=>{
        const e=document.getElementById('aib-practice-20261031');
        return {path:location.pathname,width:innerWidth,body:document.body.scrollWidth,
          route:!!document.getElementById('aib-learning-route'),
          exercise:!!e,exerciseVisible:e?!!(e.offsetWidth||e.offsetHeight):null,
          fakeHeadings:[...document.querySelectorAll('h1,h2')].filter(x=>x.textContent.includes('{title}')).length};
      });
      if(result.fakeHeadings)throw Error('Literal HTML rendered as headings: '+file);
      if(file!=='start-here.html'&&(!result.route||!result.exercise||result.exerciseVisible))throw Error('Missing learning route or paid exercise is visible: '+file);
      results.push(result);
    }
  }
  await page.goto('http://127.0.0.1:8937/start-here.html');
  await page.getByText('정답과 완료 기준 확인',{exact:true}).click();
  if(!await page.getByText('30,000원 → 35,000원으로 수정합니다.',{exact:true}).isVisible())throw Error('Answer key unavailable');
  await page.locator('textarea').first().fill('가상 안내 초안 만들기');
  if(await page.locator('textarea').first().inputValue()!=='가상 안내 초안 만들기')throw Error('Worksheet failed');
  return {readerChecks:results,answerKey:'PASS',worksheet:'PASS'};
}
