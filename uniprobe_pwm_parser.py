import re
from os.path import join

def pwm_parser(folder, pwm):
    pwm_file_to_read = join(folder, pwm)
    with open(pwm_file_to_read) as pwm:
        pwmDict = {}
        nucs = pwm.readlines()
        if 'bml' in pwm:
            try:
                pwmDict['A'] = re.findall('\d\.\d+', nucs[2])
                pwmDict['C'] = re.findall('\d\.\d+', nucs[3])
                pwmDict['G'] = re.findall('\d\.\d+', nucs[4])
                pwmDict['T'] = re.findall('\d\.\d+', nucs[5])
            except:
                pwmDict['A'] = re.findall('\d\.\d+', nucs[1])
                pwmDict['C'] = re.findall('\d\.\d+', nucs[2])
                pwmDict['G'] = re.findall('\d\.\d+', nucs[3])
                pwmDict['T'] = re.findall('\d\.\d+', nucs[4])

        else:
            for i, line in enumerate(nucs):
                if re.search('probability', line, flags = re.I):
                    pwmDict['A'] = re.findall('\d\.\d+', nucs[i+2])
                    pwmDict['C'] = re.findall('\d\.\d+', nucs[i+3])
                    pwmDict['G'] = re.findall('\d\.\d+', nucs[i+4])
                    pwmDict['T'] = re.findall('\d\.\d+', nucs[i+5])

    return pwmDict
