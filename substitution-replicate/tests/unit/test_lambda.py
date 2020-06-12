from main import lambda_handler


class TestLambda:
    def test_mappings(self):
        result = lambda_handler(
            {
                'requestId': 'one',
                'fragment': {
                    'AWSTemplateFormatVersion': '2010-09-09',
                    'Mappings': {
                        'stacks': {
                            'one': {
                                'url': 'production.yml',
                                'version': 2
                            },
                            'two': {
                                'url': 'development.yml'
                            }
                        }
                    },
                    'Resources': {
                        'BaseStack': {
                            'Type': 'AWS::CloudFormation::Stack',
                            'SubReplicate': 'stacks',
                            'Properties': {
                                'TemplateURL': {
                                    'Fn::Sub': [
                                        '${url}-${version}',
                                        {
                                            'version': 1
                                        }
                                    ]
                                }
                            }
                        },
                        'OtherStack': {
                            'Type': 'AWS::CloudFormation::Stack',
                            'Properties': {
                                'TemplateURL': 'template.yml',
                            }
                        }
                    }
                }
            }, None
        )

        assert result == {
            'requestId': 'one',
            'status': 'success',
            'fragment': {
                'AWSTemplateFormatVersion': '2010-09-09',
                'Mappings': {
                    'stacks': {
                        'one': {
                            'url': 'production.yml',
                            'version': 2
                        },
                        'two': {
                            'url': 'development.yml'
                        }
                    }
                },
                'Resources': {
                    'BaseStackOne': {
                        'Type': 'AWS::CloudFormation::Stack',
                        'Properties': {
                            'TemplateURL': {
                                'Fn::Sub': [
                                    '${url}-${version}',
                                    {
                                        'url': 'production.yml',
                                        'version': 2
                                    }
                                ]
                            }
                        }
                    },
                    'BaseStackTwo': {
                        'Type': 'AWS::CloudFormation::Stack',
                        'Properties': {
                            'TemplateURL': {
                                'Fn::Sub': [
                                    '${url}-${version}',
                                    {
                                        'url': 'development.yml',
                                        'version': 1
                                    }
                                ]
                            }
                        }
                    },
                    'OtherStack': {
                        'Type': 'AWS::CloudFormation::Stack',
                        'Properties': {
                            'TemplateURL': 'template.yml',
                        }
                    }
                }
            }
        }

    def test_inline(self):
        result = lambda_handler(
            {
                'requestId': 'one',
                'fragment': {
                    'AWSTemplateFormatVersion': '2010-09-09',
                    'Resources': {
                        'BaseStack': {
                            'Type': 'AWS::CloudFormation::Stack',
                            'SubReplicate': {
                                'one': {
                                    'url': 'production.yml',
                                    'version': 2
                                },
                                'two': {
                                    'url': 'development.yml'
                                }
                            },
                            'Properties': {
                                'TemplateURL': {
                                    'Fn::Sub': [
                                        '${url}-${version}',
                                        {
                                            'version': 1
                                        }
                                    ]
                                }
                            }
                        },
                        'OtherStack': {
                            'Type': 'AWS::CloudFormation::Stack',
                            'Properties': {
                                'TemplateURL': 'template.yml',
                            }
                        }
                    }
                }
            }, None
        )

        assert result == {
            'requestId': 'one',
            'status': 'success',
            'fragment': {
                'AWSTemplateFormatVersion': '2010-09-09',
                'Resources': {
                    'BaseStackOne': {
                        'Type': 'AWS::CloudFormation::Stack',
                        'Properties': {
                            'TemplateURL': {
                                'Fn::Sub': [
                                    '${url}-${version}',
                                    {
                                        'url': 'production.yml',
                                        'version': 2
                                    }
                                ]
                            }
                        }
                    },
                    'BaseStackTwo': {
                        'Type': 'AWS::CloudFormation::Stack',
                        'Properties': {
                            'TemplateURL': {
                                'Fn::Sub': [
                                    '${url}-${version}',
                                    {
                                        'url': 'development.yml',
                                        'version': 1
                                    }
                                ]
                            }
                        }
                    },
                    'OtherStack': {
                        'Type': 'AWS::CloudFormation::Stack',
                        'Properties': {
                            'TemplateURL': 'template.yml',
                        }
                    }
                }
            }
        }
