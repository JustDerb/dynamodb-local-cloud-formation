#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import os
import re


class CloudFormationFnResolver:
    def resolve(self, jsonResource):
        # We only care about dict objects below, so short circuit
        if not isinstance(jsonResource, dict):
            return jsonResource

        # Some of these, we skip because they are hard to "resolve" (Fn::ImportValue).
        # For others, they are just not implemented...
        for key in jsonResource:
            lkey = key.lower()
            if lkey == 'fn::base64':
                jsonResource = self.process_fnbase64(jsonResource[key])
            elif lkey == 'fn::cidr':
                print 'Encountered Fn::Cidr - skipping!'
            elif lkey == 'fn::findinmap':
                print 'Encountered Fn::FindInMap - skipping!'
            elif lkey == 'fn::getatt':
                print 'Encountered Fn::GetAtt - skipping!'
            elif lkey == 'fn::getazs':
                print 'Encountered Fn::GetAZs - skipping!'
            elif lkey == 'fn::importvalue':
                print 'Encountered Fn::ImportValue - skipping!'
            elif lkey == 'fn::join':
                print 'Encountered Fn::Join - skipping!'
            elif lkey == 'fn::select':
                print 'Encountered Fn::Select - skipping!'
            elif lkey == 'fn::split':
                print 'Encountered Fn::Split - skipping!'
            elif lkey == 'fn::sub':
                jsonResource = self.process_fnsub(jsonResource[key])
            elif lkey == 'fn::transform':
                print 'Encountered Fn::Transform - skipping!'
            elif lkey == 'ref':
                print 'Encountered Ref - skipping!'
            else:
                jsonResource[key] = self.resolve(jsonResource[key])

        return jsonResource


    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-base64.html
    def process_fnbase64(self, text):
        return base64.standard_b64encode(text)


    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html
    def process_fnsub(self, jsonResource):
        dollar_variable = '\$\{([\w\.]+)\}'
        # No mapping
        if isinstance(jsonResource, str):
            return re.sub(dollar_variable,
                    lambda match: self.sub_string(match.group(1), {}),
                    jsonResource)
        elif isinstance(jsonResoucre, dict):
            return re.sub(dollar_variable,
                    lambda match: self.sub_string(match.group(1), jsonResource[1]),
                    jsonResource[0])
        else:
            raise 'Unexpected instance type: %s' % type(jsonResource)


    def sub_string(self, text, varMap):
        if text in varMap:
            return varMap[text]
        elif os.environ.get(text):
            return os.environ.get(text)
        else:
            print 'WARNING: Replacing ${%s} with an empty string (no value in Fn::Sub map or Environment)!' % text
            return ''
