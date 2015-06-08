import json


def cloudformation_json(ami, instance_type, 
                        keyname, description, 
                        server_type='AWS::EC2::Instance', 
                        template_version='2010-09-09'):
    properties = {'ImageId': ami,
                  'InstanceType': instance_type,
                  'KeyName': keyname
                  }
    cf_content = {'AWSTemplateFormatVersion': template_version,
                  'Description': description,
                  'Resources': {'NewServer': {'Type': server_type,
                                              'Properties': properties
                                              }
                                }
                  }
    cf_json = json.dumps(cf_content)
    return cf_json
    
    
def write_json_to_file(json, target):
    with open(target, 'w') as t:
        t.write(json)
    return aws_filepath(target)
    

def aws_filepath(filepath):
    replaced_backslashes = filepath.replace('\\', '//')
    full_path = 'file://{0}'.format(replaced_backslashes)
    return full_path