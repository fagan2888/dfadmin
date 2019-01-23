'''DfAdmin Django models'''
# from django.contrib.auth.models import User
from django.core.validators import RegexValidator, URLValidator, EmailValidator
from django.db import models
from django.db.models import Max, Q
from django.utils import timezone
# from django.db.models import FileField
from django.conf import settings
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
import unicodedata
from datetime import date
import hashlib

CHAR_FIELD_MAX_LENGTH = settings.CHAR_FIELD_MAX_LENGTH
TEXT_FIELD_MAX_LENGTH = settings.TEXT_FIELD_MAX_LENGTH

MISSING_INFO_FLAG = '_Undefined_'
SEARCH_HELP_TEXT = 'Enter Text to Search'


class LdapObject(models.Model):
    ''' Django Model LdapObject
        This class represents an object on LDAP.
        The models which are syncronized to LDAP should implement this class.
    '''
    MIN_LDAP_UID = 1000
    ldap_id_help = 'This is an internal LDAP information. ' \
                   'Is it automatically generated.' \
                   'Don`t change this value unless you know what you`re doing.'
    ldap_id = models.IntegerField(blank=True,
                                  null=True,
                                  unique=True,
                                  help_text=ldap_id_help,
                                  editable=False)
    LDAP_NAME_HELP = 'Ldap_name should not have spaces or any special characters. ' \
                     'It should have at least 5 characters consisting of: letters, numbers ' \
                     'and "_" (underline). ' \
                     '<br/> If left blank, it will be automatically generated.' \
                     '<br/><b>DO NOT CHANGE THIS VALUE AFTER THE OBJECT IS CREATED ON LDAP.</b>'
    LDAP_NAME_ERROR_MESSAGES = {'invalid': 'LDAP_NAME should contain at least 5 of the following: '
                                           'letters, numbers or "_" (underline).'}
    ldap_name = models.CharField(blank=True,
                                 max_length=CHAR_FIELD_MAX_LENGTH,
                                 unique=True,
                                 null=True,
                                 validators=[RegexValidator(regex="^[a-z0-9_-]{5,}$")],
                                 error_messages=LDAP_NAME_ERROR_MESSAGES,
                                 help_text=LDAP_NAME_HELP)

    def ldap_full_dn(self):
        raise NotImplementedError("ldap_full_dn() in LDapObject is not implemented.")

    def prepare_ldap_name(self):
        ''' Prepares the ldap_name protecting against collisions.'''
        self.ldap_name = slugify(self.ldap_name.replace(' ','').lower())
        # Normalize non ASCII to ASCII
        self.ldap_name = unicodedata.normalize('NFD', self.ldap_name).encode('ascii', 'ignore')
        count = 0
        base_ldap_name = self.ldap_name
        while True:
            if self.__class__.objects.filter(ldap_name=self.ldap_name).count() > 0:
                count += 1
                self.ldap_name = base_ldap_name + str(count)
            else:
                break

    def save(self, *args, **kwargs):
        if self.ldap_id is None:
            max_id = LdapObject.objects.all().aggregate(Max('ldap_id')).values()[0]
            if max_id is None:
                # Not 1 to be different than system default users/groups.
                self.ldap_id = LdapObject.MIN_LDAP_UID
            else:
                self.ldap_id = max_id + 1
        if not self.id:
            self.prepare_ldap_name()
        super(LdapObject, self).save(*args, **kwargs)

    def __str__(self):
        return '(%s) %s' % (self.ldap_id, self.ldap_name)


class ProfileTag(models.Model):
    ''' Profile tags are used to describe users, such as tech-savy/non-tech-savy, CS-backgrund, etc.
        This should facilitate and improve communication with users.
    '''
    text = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return  self.text + ' ' + self.description

    class Meta:
        ordering = ['text']


class DfRole(LdapObject):
    '''
        Data Facility Role represents the real life role that users can have on the DF, such as
        Student, Researcher or Staff.
        The roles should never be deleted to keep the history of roles a user had.
    '''
    ADRF_CURATORS = 'ADRF Curators'
    ADRF_CURATORS_DESCRIPTION = 'ADRF Data Curators'

    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, null=True, blank=True)

    # Automatic Fields + audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def active_users(self):
        '''return a list of all active users checking their statuses.'''
        # TODO: this method should be renamed to active_user_df_roles
        return UserDfRole.objects.filter(Q(role=self,
                                    begin__lte=timezone.now(),
                                    user__status__in=User.MEMBERSHIP_STATUS_WHITELIST),
                                    Q(end__isnull=True) | Q(end__gt=timezone.now()))

    def active_usernames(self):
        '''return a list of all active users checking their statuses.'''
        # TODO: this method should be renamed to active_user_df_roles
        return [u for u in self.active_users().values_list('user__ldap_name', flat=True)]


    def ldap_full_dn(self):
        return "cn={0},{1},{2}".format(self.ldap_name,
                                       settings.LDAP_SETTINGS['Groups']['BaseDn'],
                                       settings.LDAP_BASE_DN)

    def save(self, *args, **kwargs):
        if not self.ldap_name:
            self.ldap_name = self.name
        super(DfRole, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Data Facility Role'
        verbose_name_plural = 'Data Facility Roles'


class SystemInfo(models.Model):
    ''' This model is internal and serves to store system information such as last sync time.'''
    last_export = models.DateTimeField(null=True, blank=True, editable=False)
    last_import = models.DateTimeField(null=True, blank=True, editable=False)


class User(LdapObject):
    ''' Represents the Data Facility User.
        Should never be deleted, but only disabled.
    '''
    # user = models.OneToOneField(User, blank=True, null=True)
    # username = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)

    first_name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    last_name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    orc_id = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    affiliation = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    email = models.EmailField(unique=True, validators=[EmailValidator])

    foreign_national = models.BooleanField(default=False)
    contractor = models.BooleanField(default=False)

    job_title = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    sponsor = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    ''' For documentation of user status and state changes, check:
     documentation/State machine diagram - User Status'''
    ''' > New: user on the system. This user that needs to be created on LDAP.
    The transition to Active is automatic from the system.'''
    STATUS_HELP_TEXT = \
    '''
    <b>Pending Approval</b>: Accounts on this status will not be created on the system. <br/>
    <b>New</b>: DFAdmin to create an account on ADRF. DFAdmin will change the status to active after account creation.
    <br/>
    <b>Active</b>: Users that can access the system. <br/>
    <b>Locked</b>: The user account is locked and will not be able to authenticate. 
        To unlock the user, set the status to unlocked.<br/>
    <b>Locked by too many failed attempts</b>: This is an automatic status and the admin should not use it.
        After the defined time, the user will return automatically to active. <br/>
    <b>Locked by inactivity</b>: This is an automatic status, the admin should not use this status. 
        To unlock the user, set the status to unlocked.<br/>
    <b>Unlocked</b>: Admins should use this status to return a user to active. 
        This can be used (1) before the automatic time, when they're locked by too many failed attempts; 
        or (2) when the user is locked by inactivity.<br/>
    <b>Disabled</b>: This status should be used instead of removing a user. <br/>
    <a target="_blank" 
     href='https://github.com/NYU-Chicago-data-facility/dfadmin/blob/master/documentation/State%20machine%20Diagram%20-%20User%20Status.jpg'>
     State machine Diagram - User Status (DFAdmin GitHub)
    </a>
    '''
    STATUS_NEW = 'New'
    STATUS_PENDING_APPROVAL = 'Pending Approval'
    STATUS_ACTIVE = 'Active'
    STATUS_LOCKED_BY_ADMIN = 'Locked'
    STATUS_LOCKED_WRONG_PASSWD = 'Locked by too many failed auth attempts'
    STATUS_LOCKED_WRONG_PASSWD_TEXT = 'Locked by too many failed auth attempts (AUTO)'
    STATUS_LOCKED_INACTIVITY = 'Locked by inactivity'
    STATUS_LOCKED_INACTIVITY_TEXT = 'Locked by inactivity (AUTO)'
    STATUS_UNLOCKED_BY_ADMIN = 'Unlocked'
    STATUS_DISABLED = 'Disabled'
    STATUS_CHOICES = (
        (STATUS_PENDING_APPROVAL, STATUS_PENDING_APPROVAL),
        (STATUS_NEW, STATUS_NEW),
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_LOCKED_BY_ADMIN, STATUS_LOCKED_BY_ADMIN),
        (STATUS_LOCKED_WRONG_PASSWD, STATUS_LOCKED_WRONG_PASSWD_TEXT),
        (STATUS_LOCKED_INACTIVITY, STATUS_LOCKED_INACTIVITY_TEXT),
        (STATUS_UNLOCKED_BY_ADMIN, STATUS_UNLOCKED_BY_ADMIN),
        (STATUS_DISABLED, STATUS_DISABLED),
    )
    status = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH,
                              choices=STATUS_CHOICES,
                              default=STATUS_NEW, help_text=STATUS_HELP_TEXT)
    MEMBERSHIP_STATUS_WHITELIST = [STATUS_ACTIVE, STATUS_LOCKED_WRONG_PASSWD,
                                   STATUS_UNLOCKED_BY_ADMIN]
    # terms = Terms of Use
    SIGNED_TERMS_HELP_TEXT = 'Indicates when the user signed the Data Facility Terms of User'
    signed_terms_at = models.DateField(blank=True, null=True, help_text=SIGNED_TERMS_HELP_TEXT)
    tags = models.ManyToManyField(ProfileTag, blank=True)

    ldap_last_auth_time = models.DateTimeField(null=True, blank=True, editable=False, verbose_name='Last Access')
    ldap_lock_time = models.DateTimeField(null=True, blank=True, editable=False)
    ldap_last_pwd_change = models.DateTimeField(null=True, blank=True, editable=False, verbose_name='Last Password Change')

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    SYSTEM_USER_HELP_TEXT = "Is it a system user?"
    system_user = models.BooleanField(default=False, help_text=SYSTEM_USER_HELP_TEXT)

    @property
    def avatar(self):
        # https://en.gravatar.com/site/implement/images/
        return "https://www.gravatar.com/avatar/%s?d=identicon&r=PG" % hashlib.md5(self.email).hexdigest()

    def save(self, *args, **kwargs):
        if not self.ldap_name:
            self.ldap_name = (self.first_name + self.last_name)
            if self.foreign_national:
                self.ldap_name += '_fr'
            if self.contractor:
                self.ldap_name += '_ctr'

        super(User, self).save(*args, **kwargs)

    def role(self):
        try:
            return UserDfRole.objects.filter(user=self, active=True).role
        except UserDfRole.DoesNotExist:
            return None

    def ldap_full_dn(self):
        return "uid={0},{1},{2}".format(self.ldap_name,
                                        settings.LDAP_SETTINGS['Users']['BaseDn'],
                                        settings.LDAP_BASE_DN)

    def username(self):
        return self.ldap_name

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def has_signed_tou(self):
        return self.signed_terms_at is not None

    def profile_tags(self):
        return ', '.join([tag.text for tag in self.tags.all()])

    """
    If it's a system user, it should use a different Password Policy configuration. Otherwise, it should use the default configuration.
    """
    def ldap_ppolicy_configuration_dn(self):
        if self.system_user and 'General' in settings.LDAP_SETTINGS and 'SystemUserPpolicyConfig' in settings.LDAP_SETTINGS['General']:
            return settings.LDAP_SETTINGS['General']['SystemUserPpolicyConfig']
        else:
            return None

    def __str__(self):
        return self.first_name + ' ' + self.last_name + " (" + self.username() + ")"

    class Meta:
        ordering = ['first_name', 'last_name']


class UserDfRole(models.Model):
    ''' Many-to-many relationship between User and Role.
        Status disabled should be used instead of remove a reccord.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(DfRole, on_delete=models.PROTECT)
    begin = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def active(self):
        if self.begin:
            if self.end:
                return (self.begin <= timezone.now() <= self.end)
            else:
                return self.begin <= timezone.now()
        else:
            return False

    def __str__(self):
        return '%s: %s (%s)' % (self.user, self.role, self.active())

    class Meta:
        ordering = ['user', 'role']
        unique_together = ('user', 'role')


class TermsOfUse(models.Model):
    ''' Data Facility Terms of Use that all Users need to sign. '''
    text = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)
    version = models.IntegerField(blank=True)
    release_date = models.DateField(auto_now_add=True, blank=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s (%s)' % (self.version, self.release_date)

    class Meta:
        ordering = ['version']


class SignedTermsOfUse(models.Model):
    ''' The TOU can have multiple versions on time.
        This model represents which TOU the user signed.
    '''
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    terms_of_use = models.ForeignKey(TermsOfUse, on_delete=models.PROTECT)
    signed_at = models.DateField()

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s - %s (%s)' % (self.user, self.terms_of_use, self.signed_at)

    class Meta:
        ordering = ['user', 'terms_of_use', 'signed_at']


class Project(LdapObject):
    ''' DF Projects can represent Class, Research Project, or Class Project.
        It has a group of users and tools associated with it.
    '''
    PROJECT_PREFIX = 'project-'
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT, help_text=SEARCH_HELP_TEXT)
    parent_project = models.ForeignKey('self', null=True, blank=True,
                                       on_delete=models.PROTECT, help_text=SEARCH_HELP_TEXT)
    # TODO: Add validation: instructors is only for project type Class
    instructors_help = '''By default, instructors have Read/Write permissions 
    to the project folder and database schema. </br>
    Any permissions granted on the project to an user that is also an instructor will be ignored.'''
    instructors = models.ForeignKey(DfRole, null=True, blank=True, on_delete=models.PROTECT,
                                    help_text=instructors_help)
    has_irb = models.BooleanField(default=False)
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    abstract = models.TextField(max_length=CHAR_FIELD_MAX_LENGTH)
    methodology = models.TextField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    expected_outcomes = models.TextField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    STATUS_NEW = 'Pending Approval'
    STATUS_ACTIVE = 'Active'
    STATUS_ARCHIVED = 'Archived'
    STATUS_CHOICES = (
        (STATUS_NEW, STATUS_NEW),
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_ARCHIVED, STATUS_ARCHIVED),
    )
    status_help = '''
    <b>Pending Approval</b>: Represents projects that are not yet approved for usage.
    These projects are ignored and will not be propagated to LDAP.
    <br/><b>Active</b>: Active projects will have database schemas and project folders created.
    <br/><b>Archived</b>: Archived projects don't have a database schema neither project folders.
    '''
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW,
                              help_text=status_help)
    PROJECT_TYPE_CLASS = 'Class'
    PROJECT_TYPE_CAPSTONE = 'Capstone'
    PROJECT_TYPE_RESEARCH = 'Research'
    PROJECT_TYPE_DATA_TRANSFER = 'Data Transfer'
    TYPE_CHOICES = (
        (PROJECT_TYPE_CAPSTONE, PROJECT_TYPE_CAPSTONE),
        (PROJECT_TYPE_CLASS, PROJECT_TYPE_CLASS),
        (PROJECT_TYPE_RESEARCH, PROJECT_TYPE_RESEARCH),
        (PROJECT_TYPE_DATA_TRANSFER, PROJECT_TYPE_DATA_TRANSFER),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=PROJECT_TYPE_RESEARCH)
    ENV_GREEN = 'Green'
    ENV_YELLOW = 'Yellow'
    ENV_RED = 'Red'
    ENV_CHOICES = (
        (ENV_GREEN, ENV_GREEN),
        (ENV_YELLOW, ENV_YELLOW),
        (ENV_RED, ENV_RED),
    )
    environment = models.CharField(max_length=10, choices=ENV_CHOICES, default=ENV_GREEN,
                                   blank=True)
    REQUEST_ID_HELP_TEXT = 'Id from the ticketing system, ' \
                           'so it is possible to trace back if more info is needed.'
    request_id = models.IntegerField(default=None, blank=True, null=True,
                                     help_text=REQUEST_ID_HELP_TEXT)
    workspace_path = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def db_schema(self):
        return self.ldap_name.replace(Project.PROJECT_PREFIX, '')

    def ldap_full_dn(self):
        return "cn={0},{1},{2}".format(self.ldap_name,
                                       settings.LDAP_SETTINGS['Projects']['BaseDn'],
                                       settings.LDAP_BASE_DN)

    def members_count(self):
        return self.projectmember_set.all().count()

    def __str__(self):
        if self.owner is not None:
            return '{0} (owned by {1})'.format(self.name, self.owner.full_name())
        return '{0} (owned by no one)'.format(self.name)

    def members(self):
        all_members = self.projectmember_set.all()
        if all_members > 0:
            members_list = [pm.member.full_name() for pm in all_members]
            members_list.sort()
            return ', '.join(members_list)
        return None

    def active_members(self):
        members = {pm.member for pm in ProjectMember.objects.filter(Q(project=self,
                            start_date__lte=timezone.now(),
                            member__status__in=User.MEMBERSHIP_STATUS_WHITELIST),
                            Q(end_date__isnull=True) | Q(end_date__gt=timezone.now()))}

        if self.instructors:
            members = members | {udr.user for udr in
                                 UserDfRole.objects.filter(Q(role=self.instructors,
                                    begin__lte=timezone.now(),
                                    user__status__in=User.MEMBERSHIP_STATUS_WHITELIST),
                                    Q(end__isnull=True) | Q(end__gt=timezone.now()))}
        return members

    def active_member_permissions(self):
        active_members = self.active_members()

        member_permissions = []
        # Project Instructors have write permissions by default.
        if self.instructors:
            for mr in self.instructors.active_users():
                member_permissions.append({'username': mr.user.username(),
                                           'system_role': ProjectRole.SYSTEM_ROLE_WRITER})
        instructor_usernames = [mp['username'] for mp in member_permissions]
        # Member permissions depend on associated project role.
        for pm in self.projectmember_set.all():
            if pm.member in active_members and pm.member.username() not in instructor_usernames:
                member_permissions.append({'username': pm.member.username(),
                                           'system_role': pm.role.system_role})

        return member_permissions

    def datasets_with_access(self):
        data_access_list = self.datasetaccess_set.all()
        active_das = [da for da in data_access_list if da.status() is DatasetAccess.STATUS_ACTIVE]
        return [da.dataset.dataset_and_schema() for da in active_das]

    def system_name(self):
        # TODO: write unit tests for this
        return slugify(self.name).replace('-', '_')

    def save(self, *args, **kwargs):
        if self.ldap_name is None:
            self.ldap_name = Project.PROJECT_PREFIX + self.system_name()
        super(Project, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class ProjectRole(models.Model):
    ''' Project roles are important as the Project Tool's permissions are based on it.
        Admin can manage the project - E.G. Add/Remove members
        Writer can change project assets, such as files or database.
        Reader can only read the project assets. They have read only access to the database
            and restricted permissions on other Tools.
    '''
    NAME_HELP_TEXT = 'This is a friendly name, such as Student (Reader) or Instructor (Admin).'
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, help_text=NAME_HELP_TEXT, unique=True)
    description = models.TextField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    # These SYSTEM_ROLES are a set of roles that the tools understand.
    # Before changing these make sure you know what the implications are.
    SYSTEM_ROLE_READER = 'Reader'
    SYSTEM_ROLE_WRITER = 'Writer'
    SYSTEM_ROLE_ADMIN = 'Admin'
    DBMS_ROLE_CHOICES = (
        (SYSTEM_ROLE_READER, SYSTEM_ROLE_READER),
        (SYSTEM_ROLE_WRITER, SYSTEM_ROLE_WRITER),
        (SYSTEM_ROLE_ADMIN, SYSTEM_ROLE_ADMIN),
    )
    system_role = models.CharField(max_length=10, choices=DBMS_ROLE_CHOICES,
                                   default=SYSTEM_ROLE_ADMIN)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ['name']


class ProjectMember(models.Model):
    ''' Represent the membership of Users on Projects. '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text=SEARCH_HELP_TEXT)
    role = models.ForeignKey(ProjectRole, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE, help_text=SEARCH_HELP_TEXT)

    def active(self):
        if self.begin:
            if self.end:
                return (self.begin <= timezone.now() <= self.end)
            else:
                return self.begin <= timezone.now()
        else:
            return False

    REQUEST_ID_HELP_TEXT = 'Id for from the ticketing system ' \
                           '(if not the same from project creation), ' \
                           'so it is possible to trace back if more info is needed.'
    request_id = models.IntegerField(default=None, blank=True, null=True,
                                     help_text=REQUEST_ID_HELP_TEXT)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '{1}: {0} ({2})'.format(self.member.full_name(), self.project, self.role.name)

    class Meta:
        ordering = ['project', 'member']


class ProjectTool(models.Model):
    ''' Project assets such as Database, Filesystem, Git repo, etc.
        The permissions ProjectMembers have depend on the ProjectRole.
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    ADDITIONAL_INFO_HELP = 'Additional info, such as database name. In case it does not follow ' \
                           'the Data Facility convention.'
    additional_info = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True,
                                       help_text=ADDITIONAL_INFO_HELP)
    REQUEST_ID_HELP_TEXT = 'Id for from the ticketing system (if not the same from project ' \
                           'creation), so it is possible to trace back if more info is needed.'
    request_id = models.IntegerField(default=None, blank=True, null=True,
                                     help_text=REQUEST_ID_HELP_TEXT)
    TOOL_GIT = 'Git Lab'
    TOOL_DATABASE_PG = 'Postgres'
    TOOL_DATABASE_ORACLE = 'Oracle'
    TOOL_FILESYSTEM = 'POSIX'
    TOOL_OTHER = 'Other'
    TOOL_CHOICES = (
        (TOOL_GIT, TOOL_GIT),
        (TOOL_DATABASE_PG, TOOL_DATABASE_PG),
        (TOOL_DATABASE_ORACLE, TOOL_DATABASE_ORACLE),
        (TOOL_FILESYSTEM, TOOL_FILESYSTEM),
        (TOOL_OTHER, TOOL_OTHER),
    )
    tool_name = models.CharField(max_length=10, choices=TOOL_CHOICES, default=TOOL_DATABASE_PG)
    other_name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True,
                                  help_text='Specify the tool name if Other is selected.')
    STATUS_ACTIVE = 'Active'
    STATUS_DEACTIVATED = 'Deactivated'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_DEACTIVATED, STATUS_DEACTIVATED),
    )
    status = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, choices=STATUS_CHOICES,
                              default=STATUS_ACTIVE)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def name(self):
        if self.tool_name is ProjectTool.TOOL_OTHER:
            return self.other_name
        return self.tool_name

    def __str__(self):
        return '%s %s %s' % (self.tool_name, self.other_name, self.additional_info)

    class Meta:
        ordering = ['tool_name', 'other_name']


class DataProvider(models.Model):
    ''' Represent the Owner of the data or the user which added the date to the System. '''
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)

    def datasets_count(self):
        return self.dataset_set.all().count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class DatabaseSchema(models.Model):
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    public = models.BooleanField(default=False, help_text='Check this if everyone should '
                                                          'have access to this schema. '
                                                          'Please consider the related dataset '
                                                          'permissions.')
    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        if self.public:
            return self.name + ' (public)'
        return self.name + ' (protected)'

    class Meta:
        ordering = ['name']


class Dataset(LdapObject):
    ''' This model will be refactored on the future to represent the whole dataset,
        considering files and variables.
    '''
    data_provider = models.ForeignKey(DataProvider, null=True, blank=True, on_delete=models.PROTECT)
    database_schema = models.ForeignKey(DatabaseSchema, null=True, blank=True,
                                        on_delete=models.PROTECT,
                                        help_text='The database schema that this dataset should be '
                                                  'stored to.')
    public = models.BooleanField(default=False, help_text='Check this if everyone should '
                                                          'have access to this dataset.')
    dataset_id = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, unique=True)
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    description = models.TextField(blank=True, null=True)
    dataset_citation = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True, default='1')
    SOURCE_ARCHIVE_HELP_TEXT = 'Represents the source archive reference for this dataset in the that we got it from ' \
                               'an archive instead of directly from the data owner/provider.'
    source_archive = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True,
                                      help_text=SOURCE_ARCHIVE_HELP_TEXT)
    SOURCE_URL_HELP_TEXT = 'Indicates the URL for the Source Archive, when this information is needed.'
    source_url = models.URLField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True,
                                  help_text=SOURCE_URL_HELP_TEXT, validators=[URLValidator])
    STORAGE_LOCATION_HELP_TEXT = 'Location of this dataset (Optional if dataset is green).'
    storage_location = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True,
                                        help_text=STORAGE_LOCATION_HELP_TEXT)
    VAULT_VOLUME_HELP_TEXT = 'Volume on DF Vault. For non green datasets only. ' \
                      'This information is internal.'
    vault_volume = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True,
                                    help_text=VAULT_VOLUME_HELP_TEXT)
    needs_review = models.BooleanField(default=False)
    shareable = models.BooleanField(default=True,
                                    help_text='Indicates if this dataset can be shared with '
                                              'other users.')
    temporal_coverage_start = models.DateField(blank=True, null=True)
    temporal_coverage_end = models.DateField(blank=True, null=True)
    data_ingested_at = models.DateField(blank=True, null=True)
    data_updated_at = models.DateField(blank=True, null=True)
    last_reported_at = models.DateField(blank=True, null=True)
    expiration = models.DateField(blank=True, null=True)
    require_ndas = models.BooleanField(default=False)
    DATA_CLASSIFICATION_GREEN = 'Green'
    DATA_CLASSIFICATION_RESTRICTED_GREEN = 'Restricted Green'
    DATA_CLASSIFICATION_YELLOW = 'Yellow'
    DATA_CLASSIFICATION_RED = 'Red'
    DATA_CLASSIFICATION_CHOICES = (
        (DATA_CLASSIFICATION_GREEN, DATA_CLASSIFICATION_GREEN),
        (DATA_CLASSIFICATION_RESTRICTED_GREEN, DATA_CLASSIFICATION_RESTRICTED_GREEN),
        (DATA_CLASSIFICATION_YELLOW, DATA_CLASSIFICATION_YELLOW),
        (DATA_CLASSIFICATION_RED, DATA_CLASSIFICATION_RED),
    )
    data_classification = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH,
                                           choices=DATA_CLASSIFICATION_CHOICES,
                                           default=DATA_CLASSIFICATION_GREEN)
    STATUS_ACTIVE = 'Active'
    STATUS_DISABLED = 'Disabled'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_DISABLED, STATUS_DISABLED),
    )
    status = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH,
                                           choices=STATUS_CHOICES,
                                           default=STATUS_DISABLED)
    REPORT_FREQUENCY_NONE = 'No Reporting Needed'
    REPORT_FREQUENCY_QUARTERLY = 'Quarterly'
    REPORT_FREQUENCY_BIANNUAL = 'Biannual'
    REPORT_FREQUENCY_ANNUAL = 'Annual'
    REPORT_FREQUENCY_CHOICES = (
        (REPORT_FREQUENCY_NONE, REPORT_FREQUENCY_NONE),
        (REPORT_FREQUENCY_QUARTERLY, REPORT_FREQUENCY_QUARTERLY),
        (REPORT_FREQUENCY_BIANNUAL, REPORT_FREQUENCY_BIANNUAL),
        (REPORT_FREQUENCY_ANNUAL, REPORT_FREQUENCY_ANNUAL),
    )
    report_frequency = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH,
                                        choices=REPORT_FREQUENCY_CHOICES,
                                        default=REPORT_FREQUENCY_NONE)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s [%s]' % (self.name, self.dataset_id)

    class Meta:
        ordering = ['name']

    def ldap_full_dn(self):
        return "uid={0},{1},{2}".format(self.ldap_name,
                                        settings.LDAP_SETTINGS['Datasets']['BaseDn'],
                                        settings.LDAP_BASE_DN)

    def db_schema_name(self):
        if self.database_schema:
            return self.database_schema.name
        return None

    def dataset_and_schema(self):
        return {'ldap_name': self.ldap_name,
                'db_schema': self.db_schema_name()}

    def active_members(self):
        members = set()
        if self.public:
            members = {member for member in
                       User.objects.filter(status__in=User.MEMBERSHIP_STATUS_WHITELIST)}
        else:
            for access in DatasetAccess.objects.filter(Q(dataset=self,
                                                project__status=Project.STATUS_ACTIVE,
                                                granted_at__lte=timezone.now()),
                                                       Q(expire_at__isnull=True) |
                                                       Q(expire_at__gt=timezone.now())):
                members = members | set(access.project.active_members())

        return members

    def curators(self):
        '''Get the list of data curators associated with the dataset.'''
        try:
            return [userdfrole.user.ldap_name
                    for userdfrole in DfRole.objects.get(name=DfRole.ADRF_CURATORS).userdfrole_set.all()]
        except DfRole.DoesNotExist:
            return []

    def curator_permissions(self):
        ''' Returns the list of curators and the permissions. This is used on the db-sync script.'''
        return [{'user': curator, 'system_role': ProjectRole.SYSTEM_ROLE_WRITER}
                for curator in self.curators()]

    def system_status(self):
        if self.expiration and timezone.now() > self.expiration:
            return Dataset.STATUS_DISABLED
        return self.status

    def save(self, *args, **kwargs):
        if self.ldap_name is None:
            self.ldap_name = self.dataset_id
        super(Dataset, self).save(*args, **kwargs)

    def active_stewards(self):
        return [s.user for s in self.datasteward_set.all() if s.is_active()]


class DataSteward(models.Model):
    ''' A User on the DF which acts on behalf of the Data Provider granting/revoking permissions.
    '''
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def is_active(self):
        today = date.today()
        return self.start_date and today >= self.start_date and (self.end_date is None or today <= self.end_date)

    def __str__(self):
        return '%s - %s (%s:%s)' % (self.dataset, self.user, self.start_date, self.end_date)

    class Meta:
        ordering = ['dataset', 'user', 'start_date', 'end_date']


class DataAgreement(models.Model):
    ''' Represent the physical Data Agreement which governs the usage of the dataset.
        In the future, we will implement a complete digital Data Agremment management and this model
        should change.
    '''
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    title = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    text = models.TextField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    internal_notes = models.TextField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    document = models.FileField(upload_to='file_upload/data_agreements',
                                max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    delete_on_expiration = models.BooleanField(default=False)
    expiration_date = models.DateField(default=None, blank=True)
    DELETION_METHOD_DELETE = 'Delete'
    DELETION_METHOD_SHRED = 'Shred'
    DELETION_METHOD_CHOICES = (
        (DELETION_METHOD_DELETE, DELETION_METHOD_DELETE),
        (DELETION_METHOD_SHRED, DELETION_METHOD_SHRED),
    )
    deletion_method = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True,
                                       choices=DELETION_METHOD_CHOICES,
                                       default=DELETION_METHOD_DELETE)

    version = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    # TODO: Add file upload here.
    # ref: https://docs.djangoproject.com/es/1.10/topics/http/file-uploads/

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s: %s (%s)' % (self.title, self.version, self.dataset)

    class Meta:
        ordering = ['dataset', 'version', 'title']


class DataAgreementSignature(models.Model):
    ''' Signature to Data Agreements. Each user on a project needs to sign to the Data Agreement
        so the project can be granted access to the data. If a user is added later, they can just
        receive access after signing the Data Agreements.
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_agreement = models.ForeignKey(DataAgreement, on_delete=models.CASCADE)
    accepted = models.BooleanField()
    date = models.DateField(auto_now_add=True)
    STATUS_TO_SIGN = 'To sign'
    STATUS_SIGNED = 'Signed'
    STATUS_CHOICES = (
        (STATUS_TO_SIGN, STATUS_TO_SIGN),
        (STATUS_SIGNED, STATUS_SIGNED),
    )
    status = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH,
                              choices=STATUS_CHOICES, default=STATUS_TO_SIGN)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s: %s' % (self.user, self.data_agreement)

    class Meta:
        ordering = ['user', 'data_agreement']
        unique_together = ('user', 'data_agreement')


class DatasetAccess(models.Model):
    ''' Access granted to a dataset for a project. All data access is granted on project basis.
    '''
    Q_ACTIVE = Q(Q(granted_at__lte=timezone.now()),
                 Q(Q(expire_at__isnull=True) | Q(expire_at__gte=timezone.now())))

    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    dataset = models.ForeignKey(Dataset, on_delete=models.PROTECT)
    STATUS_REGISTERED = 'Registered'
    STATUS_REQUESTED = 'Requested'
    STATUS_APPROVED = 'Approved'
    STATUS_ACTIVE = 'Active'
    STATUS_DISABLED = 'Disabled'
    STATUS_CHOICES = (
        (STATUS_REQUESTED, STATUS_REQUESTED),
        (STATUS_APPROVED, STATUS_APPROVED),
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_DISABLED, STATUS_DISABLED),
    )
    #status = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, choices=STATUS_CHOICES,
    #                          default=STATUS_APPROVED)
    REQUEST_ID_HELP_TEXT = 'Id for from the ticketing system, ' \
                           'so it is possible to trace back if more info is needed.'
    request_id = models.IntegerField(default=None, blank=True, null=True,
                                     help_text=REQUEST_ID_HELP_TEXT)
    requested_at = models.DateTimeField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    granted_at = models.DateTimeField(blank=True, null=True)
    expire_at = models.DateTimeField(blank=True, null=True)
    MOTIVATION_HELP_TEXT = 'The reason of this request.'
    motivation = models.TextField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True,
                                  help_text=MOTIVATION_HELP_TEXT)
    load_to_database = models.BooleanField(default=False, blank=True)
    database_name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    schema = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True)
    STATUS_DB_REQUESTED = 'Requested'
    STATUS_DB_LOADED = 'Loaded'
    STATUS_CHOICES = (
        (STATUS_DB_REQUESTED, STATUS_DB_REQUESTED),
        (STATUS_DB_LOADED, STATUS_DB_LOADED),
    )
    database_status = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH, choices=STATUS_CHOICES,
                                       default=STATUS_DB_REQUESTED)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def status(self):
        if self.dataset.system_status() is not Dataset.STATUS_ACTIVE:
            return DatasetAccess.STATUS_DISABLED

        if self.expire_at and timezone.now() > self.expire_at:
            return DatasetAccess.STATUS_DISABLED
        elif self.granted_at and self.expire_at and (self.granted_at <= timezone.now() <= self.expire_at):
            return DatasetAccess.STATUS_ACTIVE
        elif self.granted_at and not self.expire_at and (self.granted_at <= timezone.now()):
            return DatasetAccess.STATUS_ACTIVE
        elif self.reviewed_at and timezone.now() > self.reviewed_at:
            return DatasetAccess.STATUS_APPROVED
        elif self.requested_at and timezone.now() > self.requested_at:
            return DatasetAccess.STATUS_REQUESTED
        else:
            return DatasetAccess.STATUS_REGISTERED

    def __str__(self):
        return 'Project %s, has access to dataset %s. (Status=%s)' % (self.project, self.dataset_id, self.status())

    class Meta:
        ordering = ['project', 'dataset_id']

    def member_url(self):
        return "ldap:///%s?%s?sub?(cn=%s)" % (
            settings.LDAP_BASE_DN, settings.LDAP_GROUP_FIELD_MEMBERS, self.project.ldap_name)


class Training(models.Model):
    ''' Data Facility Trainings such as privacy. '''
    name = models.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    url = models.URLField(max_length=CHAR_FIELD_MAX_LENGTH, blank=True, null=True,
                          help_text='Training website, if any.', validators=[URLValidator])
    description = models.TextField(blank=True, null=True, max_length=CHAR_FIELD_MAX_LENGTH)
    date = models.DateTimeField(blank=True, null=True)

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s: %s' % (self.name, self.date)

    class Meta:
        ordering = ['name', 'date']


class UserTraining(models.Model):
    ''' Indicates that a given user took training. '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True, help_text='When this training was taken, for '
                                                             'trainings without a specific date.')

    # Automatic Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return '%s - %s' % (self.user, self.training)

    class Meta:
        ordering = ['date', 'user', 'training']