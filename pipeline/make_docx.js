const fs = require('fs');
const D = require('docx');
const {Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow,
       TableCell, WidthType, ShadingType, BorderStyle, PageBreak, TableOfContents,
       Header, Footer, PageNumber, convertMillimetersToTwip} = D;

const IN = JSON.parse(fs.readFileSync('docx_input.json','utf8'));
const BLUE='1F4E9C', INK='14181F', SOFT='3A4049', GREY='6E6E6E', RULE='C8CCD2', TINT='F2F4F7';
const MOD_COLOUR = {'SHALL':BLUE,'SHALL NOT':'8C1D18','MAY':'00707A','DEFINITION':GREY,
  'COMMISSION MANDATE':'8A5300','REFERENCING PROVISION':'5B3E96','LEGAL EFFECT':INK};

const TEXT_W = 9638;                       // A4 minus 2 cm margins, in DXA
const label = (t) => new TextRun({text:t+'  ', bold:true, size:14, color:GREY,
                                  characterSpacing:12});
const p = (o) => new Paragraph(o);
const spacer = (n=80) => p({spacing:{after:n}, children:[]});

function fieldPara(name, text, opts={}) {
  return p({spacing:{after:60}, indent:{left:0},
    children:[label(name), new TextRun({text, size:opts.size||18, italics:!!opts.italics,
      color:opts.color||INK, font:opts.font})]});
}

function blockParas(b) {
  const out=[];
  const modColour = MOD_COLOUR[b.modality] || GREY;
  out.push(p({heading:HeadingLevel.HEADING_3, spacing:{before:260, after:60},
    children:[ new TextRun({text:b.id, font:'Consolas', size:18, color:GREY}),
               new TextRun({text:'   '+b.topic, bold:true, size:22, color:INK}) ]}));
  out.push(p({spacing:{after:100}, children:[
    new TextRun({text:' '+(b.modality||'—')+' ', bold:true, size:14, color:'FFFFFF',
                 shading:{type:ShadingType.CLEAR, fill:modColour}}),
    new TextRun({text:'   '+(b.level||''), bold:true, size:14, color:GREY})]}));
  if (b.addressee) out.push(fieldPara('ADDRESSEE', b.addressee, {italics:true, color:SOFT}));
  if (b.content)   out.push(fieldPara('CONTENT', b.content));
  if (b.purpose)   out.push(fieldPara('PURPOSE', b.purpose, {italics:true}));
  if (b.deadline)  out.push(fieldPara('DEADLINE', b.deadline, {font:'Consolas', size:17}));
  if (b.refs && b.refs.length) {
    out.push(p({spacing:{before:100, after:40}, children:[label('CROSS-REFERENCES')]}));
    for (const r of b.refs) {
      const head=[new TextRun({text:r.cite||'—', bold:true, size:17, color:BLUE})];
      if (r.title) head.push(new TextRun({text:'  '+r.title, bold:true, size:17, color:INK}));
      out.push(p({spacing:{before:60, after:20}, indent:{left:340}, children:head}));
      if (r.gloss) out.push(p({spacing:{after:20}, indent:{left:340},
        children:[new TextRun({text:r.gloss, size:16, color:SOFT})]}));
      if (r.quote) {
        out.push(p({spacing:{after:20}, indent:{left:680},
          border:{left:{style:BorderStyle.SINGLE, size:10, color:BLUE, space:6}},
          children:[new TextRun({text:'“'+r.quote+'”', size:17, font:'Georgia'})]}));
        out.push(p({spacing:{after:20}, indent:{left:680}, children:[
          new TextRun({text:(r.mark||'✓')+' '+(r.qcite||''), size:14, color:BLUE})]}));
      } else if (r.mark==='●') {
        out.push(p({spacing:{after:20}, indent:{left:680}, children:[
          new TextRun({text:'● summary, not verified against the original', size:14, color:GREY})]}));
      }
      if (r.relevance) out.push(p({spacing:{after:20}, indent:{left:340}, children:[
        new TextRun({text:'Relevance: ', bold:true, size:16, color:SOFT}),
        new TextRun({text:r.relevance, size:16, color:SOFT})]}));
    }
  }
  if (b.keypoint) out.push(p({spacing:{before:100, after:160},
    shading:{type:ShadingType.CLEAR, fill:TINT},
    children:[label('KEY POINT'), new TextRun({text:b.keypoint, bold:true, size:19, color:INK})]}));
  return out;
}
module.exports = {D, IN, BLUE, INK, SOFT, GREY, RULE, TINT, TEXT_W, p, label, spacer, blockParas};
