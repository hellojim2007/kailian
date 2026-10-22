"""Small authoring helpers for independent, cumulative assessments."""
import textwrap


def source(code):
    return textwrap.dedent(code).strip() + '\n'


def check(expr, expected=None, *, setup=None, raises=None, label='边界检查', tolerance=None):
    result={'expr':expr,'expected':expected,'label':label}
    if setup: result['setup']=source(setup)
    if raises: result['raises']=raises
    if tolerance is not None: result['tolerance']=tolerance
    return result


class Bank:
    def __init__(self, prefix):
        self.prefix=prefix
        self.items=[]
        self.exercises=[]
        self.exams=[]
        self.reviewItems=[]

    def _item(self, key, chapter, kind, prompt, explanation, skills, points):
        item={'id':f'ax-{self.prefix}-{key}','chapter':chapter,'kind':kind,
              'prompt':prompt,'explanation':explanation,'skills':skills,'points':points}
        self.items.append(item)
        return item

    def output(self,key,chapter,prompt,code,expected,explanation,skills,points=2,runtime='python'):
        item=self._item(key,chapter,'output',prompt,explanation,skills,points)
        item.update(code=source(code),expectedStdout=expected,runtime=runtime)
        return item['id']

    def choice(self,key,chapter,prompt,options,answer,explanation,skills,points=1,code=None):
        item=self._item(key,chapter,'choice',prompt,explanation,skills,points)
        # Stable variation prevents a fixed-position shortcut.
        shift=sum(map(ord,item['id']))%len(options)
        item.update(options=options[shift:]+options[:shift],answer=(answer-shift)%len(options),runtime='python')
        if code: item['code']=source(code)
        return item['id']

    def coding(self,key,chapter,prompt,signature,solution,tests,explanation,skills,points=4,runtime='python',fixtures=None):
        item=self._item(key,chapter,'code',prompt,explanation,skills,points)
        exercise={'id':item['id'],'runtime':runtime,'task':prompt,'signature':signature,
                  'solution':source(solution),'tests':tests}
        if fixtures: exercise['fixtures']=fixtures
        self.exercises.append(exercise)
        item.update(exerciseId=item['id'],signature=signature,runtime=runtime)
        return item['id']

    def exam(self,key,kind,title,chapters,minutes,items,description):
        self.exams.append({'id':key,'kind':kind,'title':title,'chapters':chapters,
                           'minutes':minutes,'itemIds':items,'description':description})

    def review(self,*item_ids):
        self.reviewItems.extend(item_ids)

    def result(self):
        return {'exams':self.exams,'items':self.items,'exercises':self.exercises,'reviewItems':self.reviewItems}
