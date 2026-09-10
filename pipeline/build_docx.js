const fs=require('fs');
const M=require('./make_docx.js');
const {D,IN,BLUE,INK,SOFT,GREY,RULE,TINT,TEXT_W,p,label,blockParas}=M;
const {Document,Packer,Paragraph,TextRun,HeadingLevel,AlignmentType,Table,TableRow,TableCell,
       WidthType,ShadingType,BorderStyle,PageBreak,TableOfContents,Header,Footer,PageNumber}=D;

const SPEC={
 C:{title:'All Articles at a Glance', sub:'Chapters I to VI and Annexes I to VII',
    heads:['Art.','Ch.','Subject','Main addressee','Deadline','Key point','Prio'],
    keys:['article','chapter','topic','addressee','deadline','key_point','priority'],
    w:[620,560,1900,1500,1500,2900,658]},
 D:{title:'Roles in the eIDAS System', sub:'Who acts, who is supervised, who benefits',
    heads:['Role','Task','Typical articles','Delimitation'],
    keys:['role','task','articles','delimitation'], w:[1500,3300,2100,2738]},
 E:{title:'Deadline Calendar', sub:'One-off dates and recurring obligations',
    heads:['Date / rhythm','Article','What must be done','Addressee','Note'],
    keys:['date','article','action','addressee','note'], w:[1400,1000,3400,1600,2238]},
 F:{title:'Signature and Seal Side by Side', sub:'What matches — and where the mirror ends',
    heads:['Subject','Signature','Seal','Common content','Difference'],
    keys:['subject','signature','seal','common','difference'], w:[1400,900,900,3200,3238]},
 H:{title:'Corrections Against the Previous Edition', sub:'What was checked against the Regulation and put right',
    heads:['Type','Reference','Subject','Previous wording','Finding'],
    keys:['kind','reference','subject','previous','finding'], w:[1200,1300,1600,2700,2838]},
};
const noBorders={top:{style:BorderStyle.NONE},bottom:{style:BorderStyle.NONE},
                 left:{style:BorderStyle.NONE},right:{style:BorderStyle.NONE}};
const cell=(txt,w,o={})=>new TableCell({width:{size:w,type:WidthType.DXA},
  margins:{top:60,bottom:60,left:80,right:80},
  shading:o.head?{type:ShadingType.CLEAR,fill:TINT}:undefined,
  borders:{...noBorders,bottom:{style:BorderStyle.SINGLE,size:4,color:RULE}},
  children:[p({children:[new TextRun({text:String(txt==null?'':txt),
    size:o.head?14:15, bold:!!o.head, color:o.head?GREY:(o.mono?INK:SOFT),
    font:o.mono?'Consolas':undefined})]})]});

function partTable(k, rows){
  const s=SPEC[k];
  const header=new TableRow({tableHeader:true,
    children:s.heads.map((h,i)=>cell(h.toUpperCase(), s.w[i], {head:true}))});
  const body=rows.map(r=>new TableRow({
    children:s.keys.map((key,i)=>cell(clean(key,r[key]), s.w[i], {mono:['article','reference','signature','seal'].includes(key)}))}));
  return new Table({columnWidths:s.w, width:{size:TEXT_W,type:WidthType.DXA},
                    rows:[header,...body]});
}
const clean=(key,v)=>{ v=String(v==null?'':v);
  if(['article','reference','signature','seal'].includes(key)) v=v.replace(/\bArticles?\s+/g,'').replace(/\bAnnex\s+/g,'Ann. ');
  if(key==='chapter') v=v.replace(/^Ch\.\s*/,'');
  return v; };

function partHeading(letter,title,sub){
  const head = letter ? `Part ${letter} — ${title}` : title;
  return [p({children:[new PageBreak()]}),
    p({heading:HeadingLevel.HEADING_1, spacing:{after:60},
       children:[new TextRun({text:head, bold:true, size:30, color:BLUE})]}),
    p({spacing:{after:240}, children:[new TextRun({text:sub, size:18, color:GREY})]})];
}

const kids=[];
// ---- title page
kids.push(p({spacing:{before:1400,after:80}, children:[new TextRun({text:'eIDAS', bold:true, size:72, color:BLUE})]}));
kids.push(p({spacing:{after:60}, children:[new TextRun({text:'Electronic Identification and Trust Services', size:30, color:INK})]}));
kids.push(p({spacing:{after:520}, children:[new TextRun({text:'STUDY AND AUDIT MANUAL · ENGLISH EDITION', size:17, color:GREY, characterSpacing:20})]}));
for (const t of ['Regulation (EU) No 910/2014, consolidated version of 18 October 2024','eIDAS and eIDAS 2.0'])
  kids.push(p({spacing:{after:100}, children:[new TextRun({text:t, size:20, color:INK})]}));
kids.push(p({spacing:{before:360,after:100}, children:[new TextRun({text:'SOURCE AND VERIFICATION', bold:true, size:15, color:GREY, characterSpacing:14})]}));
for (const t of [
  'Passages marked ✓ are reproduced verbatim from the official English text and were checked character for character; they are not translations made for this edition.',
  'Defined terms follow the 57 definitions of Article 3. “Wallet” is used throughout for the European Digital Identity Wallet.',
  'This document has no legal effect. Only the text published in the Official Journal of the European Union is authentic.'])
  kids.push(p({spacing:{after:90}, children:[new TextRun({text:t, size:17, color:SOFT})]}));
// ---- contents
kids.push(p({children:[new PageBreak()]}));
kids.push(p({heading:HeadingLevel.HEADING_1, spacing:{after:180},
  children:[new TextRun({text:'Contents', bold:true, size:30, color:BLUE})]}));
kids.push(new TableOfContents('Contents', {hyperlink:true, headingStyleRange:'1-3'}));
// ---- legend
kids.push(...partHeading('','How to read a norm block','Modality is a coloured tag; priority is L1 to L3'));
for (const [m,txt] of [['SHALL','Unconditional duty.'],['SHALL NOT','Prohibition.'],
  ['MAY','Discretion or a right; no duty unless exercised.'],
  ['DEFINITION','Defines a term; imposes no duty. The most common source of error.'],
  ['COMMISSION MANDATE','Empowerment to adopt an implementing or delegated act.'],
  ['REFERENCING PROVISION','Applies other articles by reference.'],
  ['LEGAL EFFECT','Non-discrimination rule or legal presumption; addressed to courts.']]) {
  kids.push(p({spacing:{after:80}, children:[
    new TextRun({text:' '+m+' ', bold:true, size:15, color:'FFFFFF',
      shading:{type:ShadingType.CLEAR, fill:(require('./make_docx.js'), {'SHALL':BLUE,'SHALL NOT':'8C1D18','MAY':'00707A','DEFINITION':GREY,'COMMISSION MANDATE':'8A5300','REFERENCING PROVISION':'5B3E96','LEGAL EFFECT':INK})[m]}}),
    new TextRun({text:'   '+txt, size:17, color:SOFT})]}));
}
for (const [l,t] of [['L1','Core material; asked in conformity assessments.'],
  ['L2','Important for understanding the system.'],['L3','Procedural and peripheral provisions.']])
  kids.push(p({spacing:{after:60}, children:[new TextRun({text:l+'   ', bold:true, size:17, color:INK}),
    new TextRun({text:t, size:17, color:SOFT})]}));
kids.push(p({spacing:{before:180,after:60}, children:[new TextRun({text:'MARKS ON A CROSS-REFERENCE', bold:true, size:15, color:GREY, characterSpacing:14})]}));
for (const [mk,t] of [['✓','Wording checked character for character against the official English text.'],
  ['●','A summary in this manual’s own words; nothing is quoted.'],
  ['(none)','The reference is explained, but no wording is quoted or asserted.']])
  kids.push(p({spacing:{after:60}, children:[new TextRun({text:mk+'   ', bold:true, size:17, color:BLUE}),
    new TextRun({text:t, size:17, color:SOFT})]}));

// ---- Parts A and B
const PART_A=new Set(['5a','5b','5c','5d','5e','5f','6','7','8','9','10','11','11a','12','12a','12b']);
for (const [letter,title,sub,pred] of [
  ['A','Electronic Identification','Chapter II · Articles 5a to 12b', b=>PART_A.has(b.article)],
  ['B','Trust Services','Chapter III · Articles 13 to 45l', b=>!PART_A.has(b.article)]]) {
  kids.push(...partHeading(letter,title,sub));
  let cur=null;
  for (const b of IN.blocks.filter(pred)) {
    if (b.article!==cur) { cur=b.article;
      kids.push(p({heading:HeadingLevel.HEADING_2, spacing:{before:320, after:100},
        children:[new TextRun({text:'Article '+cur, bold:true, size:24, color:INK})]})); }
    kids.push(...blockParas(b));
  }
}
// ---- Parts C to H
for (const k of ['C','D','E','F','G','H']) {
  const part=IN.parts[k]; if(!part) continue;
  if (k==='G') {
    kids.push(...partHeading('G','Retrieval Cards','Cover the answer, respond, then compare'));
    for (const r of part.rows) {
      kids.push(p({spacing:{before:160,after:40}, children:[
        new TextRun({text:(r.number||'')+'   ', bold:true, size:18, color:BLUE}),
        new TextRun({text:r.question||'', bold:true, size:19, color:INK}),
        new TextRun({text:'   '+(r.difficulty||'').toUpperCase(), size:13, color:GREY})]}));
      kids.push(p({spacing:{after:60}, border:{top:{style:BorderStyle.DASHED,size:4,color:RULE,space:4}},
        children:[new TextRun({text:r.answer||'', size:18, color:SOFT})]}));
    }
  } else {
    const s=SPEC[k];
    kids.push(...partHeading(k,s.title,s.sub));
    kids.push(partTable(k, part.rows));
  }
}
// ---- Part I
if (IN.parts.I) {
  kids.push(...partHeading('I','Reference Digest','What each provision says, ordered for lookup'));
  for (const e of IN.parts.I.rows) {
    kids.push(p({spacing:{before:140,after:30}, children:[new TextRun({text:e.ref, bold:true, size:18, color:BLUE})]}));
    kids.push(p({spacing:{after:40}, children:[new TextRun({text:e.text, size:17, color:SOFT})]}));
  }
}

const doc=new Document({
  creator:'eIDAS Study Manual', title:'eIDAS — Study and Audit Manual, English Edition',
  description:'Regulation (EU) No 910/2014, consolidated 18 October 2024',
  styles:{default:{document:{run:{font:'Calibri', size:19, color:INK}}}},
  features:{updateFields:true},
  sections:[{
    properties:{page:{margin:{top:1134,bottom:1134,left:1134,right:1134}}},
    headers:{default:new Header({children:[p({alignment:AlignmentType.RIGHT,
      children:[new TextRun({text:'eIDAS · Study and Audit Manual · English Edition', size:14, color:GREY})]})]})},
    footers:{default:new Footer({children:[p({alignment:AlignmentType.RIGHT,
      children:[new TextRun({children:[PageNumber.CURRENT], size:15, color:GREY})]})]})},
    children:kids}]});

Packer.toBuffer(doc).then(buf=>{
  fs.writeFileSync('eIDAS_Study_Manual_EN.docx', buf);
  console.log('written eIDAS_Study_Manual_EN.docx', (buf.length/1024/1024).toFixed(2)+' MB',
              '| paragraphs ~'+kids.length);
});
