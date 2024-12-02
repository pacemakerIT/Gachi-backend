# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Favourite(models.Model):
    favouriteid = models.UUIDField(db_column='favouriteId', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userId')  # Field name made lowercase.
    programid = models.ForeignKey('Program', models.DO_NOTHING, db_column='programId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Favourite'


class Feedback(models.Model):
    content = models.TextField()
    rating = models.FloatField(blank=True, null=True)
    feedbackid = models.UUIDField(db_column='feedbackId', primary_key=True)  # Field name made lowercase.
    mentorid = models.ForeignKey('User', models.DO_NOTHING, db_column='mentorId')  # Field name made lowercase.
    menteeid = models.ForeignKey('User', models.DO_NOTHING, db_column='menteeId', related_name='feedback_menteeid_set')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Feedback'


class Industry(models.Model):
    title = models.CharField(max_length=50)
    industryid = models.UUIDField(db_column='industryId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Industry'


class Mentormatching(models.Model):
    datetime = models.DateTimeField(db_column='dateTime')  # Field name made lowercase.
    meetingurl = models.CharField(max_length=100, db_column='meetingUrl', blank=True, null=True)  # Field name made lowercase.
    matchingid = models.UUIDField(db_column='matchingId', primary_key=True)  # Field name made lowercase.
    hostid = models.ForeignKey('User', models.DO_NOTHING, db_column='hostId')  # Field name made lowercase.
    guestid = models.ForeignKey('User', models.DO_NOTHING, db_column='guestId', related_name='mentormatching_guestid_set')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'MentorMatching'


class Note(models.Model):
    content = models.TextField()
    createdat = models.DateTimeField(db_column='createdAt', blank=True, null=True)  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt', blank=True, null=True)  # Field name made lowercase.
    noteid = models.UUIDField(db_column='noteId', primary_key=True)  # Field name made lowercase.
    adminid = models.ForeignKey('User', models.DO_NOTHING, db_column='adminId')  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userId', related_name='note_userid_set')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Note'


class Payment(models.Model):
    paymentdate = models.DateTimeField(db_column='paymentDate')  # Field name made lowercase.
    cost = models.BigIntegerField(blank=True, null=True)
    paymentid = models.UUIDField(db_column='paymentId', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userId')  # Field name made lowercase.
    paymentmethodid = models.ForeignKey('Paymentmethod', models.DO_NOTHING, db_column='paymentMethodId')  # Field name made lowercase.
    programid = models.ForeignKey('Program', models.DO_NOTHING, db_column='programId')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Payment'


class Paymentmethod(models.Model):
    paymentmethod = models.CharField(max_length=20, db_column='paymentMethod')  # Field name made lowercase.
    paymentmethodid = models.UUIDField(db_column='paymentMethodId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'PaymentMethod'


class Program(models.Model):
    title = models.CharField(max_length=20)
    datetime = models.TimeField(db_column='dateTime', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='createdAt', blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)
    programid = models.UUIDField(db_column='programId', primary_key=True)  # Field name made lowercase.
    thumbnailurl = models.TextField(db_column='thumbnailUrl', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Program'


class Programparticipants(models.Model):
    programid = models.ForeignKey(Program, models.DO_NOTHING, db_column='programId')  # Field name made lowercase.
    hostid = models.ForeignKey('User', models.DO_NOTHING, db_column='hostId')  # Field name made lowercase.
    guestid = models.ForeignKey('User', models.DO_NOTHING, db_column='guestId', related_name='programparticipants_guestid_set', blank=True, null=True)  # Field name made lowercase.
    dateofparticipant = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'ProgramParticipants'


class Programtopic(models.Model):
    programid = models.ForeignKey(Program, models.DO_NOTHING, db_column='programId')  # Field name made lowercase.
    topicid = models.ForeignKey('Topic', models.DO_NOTHING, db_column='topicId')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'ProgramTopic'


class Review(models.Model):
    content = models.TextField()
    rating = models.FloatField(blank=True, null=True)
    reviewid = models.UUIDField(db_column='reviewId', primary_key=True)  # Field name made lowercase.
    programid = models.ForeignKey(Program, models.DO_NOTHING, db_column='programId')  # Field name made lowercase.
    reviewerid = models.ForeignKey('User', models.DO_NOTHING, db_column='reviewerId')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Review'


class Test(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    age = models.SmallIntegerField(blank=True, null=True)
    img_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Test'
        db_table_comment = 'test table'


class Topic(models.Model):
    description = models.TextField()
    topicid = models.UUIDField(db_column='topicId', primary_key=True)  # Field name made lowercase.
    class Meta:
        managed = True
        db_table = 'Topic'


class User(models.Model):
    firstname = models.CharField(max_length=10, db_column='firstName')  # Field name made lowercase.
    lastname = models.CharField(max_length=10, db_column='lastName')  # Field name made lowercase.
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=20, blank=True, null=True)
    careergoal = models.CharField(max_length=20, db_column='careerGoal', blank=True, null=True)  # Field name made lowercase.
    photourl = models.TextField(db_column='photoUrl', blank=True, null=True)  # Field name made lowercase.
    linkedinurl = models.TextField(db_column='linkedInUrl', blank=True, null=True)  # Field name made lowercase.
    userid = models.UUIDField(db_column='userId', primary_key=True)  # Field name made lowercase.
    industryid = models.ForeignKey(Industry, models.DO_NOTHING, db_column='industryId', blank=True, null=True)  # Field name made lowercase.
    usertypeid = models.ForeignKey('Usertype', models.DO_NOTHING, db_column='userTypeId', blank=True, null=True)  # Field name made lowercase.
    memo = models.TextField(blank=True, null=True)
    dateofregistration = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'User'


class Usertopic(models.Model):
    userid = models.ForeignKey(User, models.DO_NOTHING, db_column='userId')  # Field name made lowercase.
    topicid = models.ForeignKey(Topic, models.DO_NOTHING, db_column='topicId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'UserTopic'


class Usertype(models.Model):
    typename = models.CharField(max_length=10, db_column='typeName')  # Field name made lowercase.
    usertypeid = models.UUIDField(db_column='userTypeId', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'UserType'






