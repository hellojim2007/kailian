import {torchLabs} from './labs-torch.js';

// Deliberate bindings only: a visual category is never enough to choose a lab.
// Keep only experiments whose changing state clarifies dimensions or training.
// Simple assignment/indexing/counting is taught with executable code instead.
export const lessonLabs=Object.freeze(Object.assign(Object.create(null),
 Object.fromEntries(['t1','t2','t3','t5','t6'].map(id=>[id,torchLabs[id]]))));
export function renderLessonLab(id){return lessonLabs[id]?.render()??'';}
export function bindLessonLab(id,root){lessonLabs[id]?.bind(root);}
