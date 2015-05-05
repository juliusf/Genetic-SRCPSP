__author__ = 'jules'
import deepThought.ORM.ORM as ORM

def main():
    job = ORM.deserialize("/tmp/output.pickle")

    results = sorted(job.tasks.values(), key=lambda x: len(x.execution_history), reverse=True)

    f = open('/tmp/data1.table','w')
    for line in results[1].execution_history:
        f.write('%s\n' % str(line)) # python will convert \n to os.linesep
    f.close()

if __name__=='__main__':
    main()