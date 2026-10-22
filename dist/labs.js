import {pythonLabs} from './labs-python.js';
import {torchLabs} from './labs-torch.js';

// Deliberate bindings only: a visual category is never enough to choose a lab.
export const lessonLabs=Object.freeze(Object.assign(Object.create(null),pythonLabs,torchLabs));
export function renderLessonLab(id){return lessonLabs[id]?.render()??'';}
export function bindLessonLab(id,root){lessonLabs[id]?.bind(root);}
