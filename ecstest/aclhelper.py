# __CR__
# Copyright (c) 2008-2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.
# __CR__

'''
Author: Rubicon ISE team
'''


def get_invalid_request_body_list(default_id):
    '''
    Give a list of typical invalid request body of ACL.

    A typical valid request body is as follows:
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>vivauser1</ID>
                <DisplayName>vivauser1</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <ID>vivauser1</ID>
                        <DisplayName>vivauser1</DisplayName>
                    </Grantee>
                    <Permission>FULL_CONTROL</Permission>
                </Grant>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Group">
                        <URI>http://acs.amazonaws.com/groups/global/AllUsers</URI>
                    </Grantee>
                    <Permission>READ</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
    See details on dev and api doc on
    http://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html
    http://docs.aws.amazon.com/AmazonS3/latest/API/RESTBucketPUTacl.html

    Note:
        Lack of DisplayName in Ownner both return 200
        on ECS and AWSS3. So skip.
        Lack of Grant in AccessControlList both return 200
        on ECS and AWSS3. So skip.
        Lack of DisplayName in Grantee of CanonicalUser
        both return 200 on ECS and AWSS3. So skip.

        Lack of namespace and invalid namespace in AccessControlPolicy
        return 400 on ECS but return 200 AWSS3.
        ECS is better than AWSS3. So skip.

        Lack of both Owner and AccessControlList in AccessControlPolicy
        return 500 on ECS but return 400 on AWSS3.
        Lack of Owner in AccessControlPolicy return 500 on ECS but return 400 on AWSS3.
        Lack of AccessControlList in AccessControlPolicy
        return 500 on ECS but return 400 on AWSS3.
        Lack of Grantee in Grant return 501 on ECS but return 400 on AWSS3.
        Only Owner return 500 on ECS but return 400 on AWSS3.

    '''
    return [
        # Empty string will return 200, so use some whitespace for test
        ' \t\n ',

        # Lack of both Owner and AccessControlList(ECS:500, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
        </AccessControlPolicy>
        ''',

        # Lack of Owner(ECS:500, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <ID>{0}</ID>
                        <DisplayName>{0}</DisplayName>
                    </Grantee>
                    <Permission>FULL_CONTROL</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Lack of AccessControlList(ECS:500, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
        </AccessControlPolicy>
        '''.format(default_id),

        # Lack of ID in Ownner(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <ID>{0}</ID>
                        <DisplayName>{0}</DisplayName>
                    </Grantee>
                    <Permission>FULL_CONTROL</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Lack of Grantee in Grant(ECS:501, AWSS3:400))
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Permission>FULL_CONTROL</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Lack of Permission in Grant(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <ID>{0}</ID>
                        <DisplayName>{0}</DisplayName>
                    </Grantee>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Lack of ID in Grantee of CanonicalUser(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                  <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <DisplayName>{0}</DisplayName>
                  </Grantee>
                  <Permission>FULL_CONTROL</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Lack of URI in Grantee of Group(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
            <ID>{0}</ID>
            <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Group">
                    </Grantee>
                    <Permission>READ</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Case problem(ECS:400, AWSS3:400)
        '''
        <accesscontrolpolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <ID>{0}</ID>
                        <DisplayName>{0}</DisplayName>
                    </Grantee>
                    <Permission>FULL_CONTROL</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Invalid Permission(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <ID>{0}</ID>
                        <DisplayName>{0}</DisplayName>
                    </Grantee>
                    <Permission>NoSuchPermission</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Invalid ID(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <ID>{0}</ID>
                        <DisplayName>{0}</DisplayName>
                    </Grantee>
                    <Permission>FULL_CONTROL</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format('nosuchid'),

        # Lack of namespace in Grantee(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xsi:type="CanonicalUser">
                        <ID>{0}</ID>
                        <DisplayName>{0}</DisplayName>
                    </Grantee>
                    <Permission>FULL_CONTROL</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Invalid namespace in Grantee(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <Owner>
                <ID>{0}</ID>
                <DisplayName>{0}</DisplayName>
            </Owner>
            <AccessControlList>
                <Grant>
                    <Grantee xmlns:xsi="http:////www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                        <ID>{0}</ID>
                        <DisplayName>{0}</DisplayName>
                    </Grantee>
                    <Permission>FULL_CONTROL</Permission>
                </Grant>
            </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Lack of type in Grantee(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
           <Owner>
               <ID>{0}</ID>
               <DisplayName>{0}</DisplayName>
           </Owner>
           <AccessControlList>
               <Grant>
                   <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                       <ID>{0}</ID>
                       <DisplayName>{0}</DisplayName>
                   </Grantee>
                   <Permission>FULL_CONTROL</Permission>
               </Grant>
           </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Invalid type in Grantee(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
           <Owner>
               <ID>{0}</ID>
               <DisplayName>{0}</DisplayName>
           </Owner>
           <AccessControlList>
               <Grant>
                   <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="nosuchtype">
                       <ID>{0}</ID>
                       <DisplayName>{0}</DisplayName>
                   </Grantee>
                   <Permission>FULL_CONTROL</Permission>
               </Grant>
           </AccessControlList>
        </AccessControlPolicy>
        '''.format(default_id),

        # Lack of AccessControlPolicy(ECS:400, AWSS3:400)
        '''
        <Owner>
            <ID>{0}</ID>
            <DisplayName>{0}</DisplayName>
        </Owner>
        <AccessControlList>
            <Grant>
                <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                    <ID>{0}</ID>
                    <DisplayName>{0}</DisplayName>
                </Grantee>
                <Permission>FULL_CONTROL</Permission>
            </Grant>
        </AccessControlList>
        '''.format(default_id),

        # Lack of close tag AccessControlPolicy(ECS:400, AWSS3:400)
        '''
        <AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
           <Owner>
               <ID>{0}</ID>
               <DisplayName>{0}</DisplayName>
           </Owner>
           <AccessControlList>
               <Grant>
                   <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                       <ID>{0}</ID>
                       <DisplayName>{0}</DisplayName>
                   </Grantee>
                   <Permission>FULL_CONTROL</Permission>
               </Grant>
           </AccessControlList>
        '''.format(default_id),

        # Only Owner(ECS:500, AWSS3:400)
        '''
        <Owner>
            <ID>{0}</ID>
            <DisplayName>{0}</DisplayName>
        </Owner>
        '''.format(default_id),

        # Only AccessControlList(ECS:400, AWSS3:400)
        '''
        <AccessControlList>
            <Grant>
                <Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">
                    <ID>{0}</ID>
                    <DisplayName>{0}</DisplayName>
                </Grantee>
                <Permission>FULL_CONTROL</Permission>
            </Grant>
        </AccessControlList>
        '''.format(default_id),

        # A xml format totally is nothing about the ACL(ECS:400, AWSS3:400)
        '''
        <doc>
           <branch name="testing" hash="1cdf045c">
               text,source
           </branch>
           <branch name="release01" hash="f200013e">
               <sub-branch name="subrelease01">
                   xml,sgml
               </sub-branch>
           </branch>
           <branch name="invalid">
           </branch>
        </doc>
        '''
    ]
