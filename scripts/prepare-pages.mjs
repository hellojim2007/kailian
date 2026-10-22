import {readdir, mkdir, copyFile, readFile, writeFile} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

// Publish only browser assets. Worker output, credentials and local records
// must never become files in the GitHub Pages artifact.
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const source=resolve(root,'dist'),out=resolve(root,'.runtime/pages');
await mkdir(out,{recursive:true});
let count=0;
for(const entry of await readdir(source,{withFileTypes:true})){
 if(entry.name.startsWith('.')||!entry.isFile())continue;
 if(!/\.(?:html|css|js|json|py|svg|txt|png|ico)$/.test(entry.name))throw new Error('Unexpected public asset '+entry.name);
 await copyFile(resolve(source,entry.name),resolve(out,entry.name));count++;
}
for(const name of ['index.html','app.js','python-worker.js','lessons.json','exams.json','grade.py','sync.js'])await readFile(resolve(out,name));
await writeFile(resolve(out,'.nojekyll'),'');
console.log(`Prepared ${count} browser assets in .runtime/pages`);
