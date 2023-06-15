# -*- coding: utf-8 -*-

{
    'name': 'Twitter Wall',
    'category': 'Odex25 Website/Website',
    'author': 'Expert Co. Ltd.',
    'website': 'http://www.exp-sa.com',
    'summary': 'Pretty Way to Display Tweets for Event',
    'description': """
Make Everybody a Part of Your Event
===================================

Turn your event into an interactive experience by letting everybody post to your Twitter Wall. Connect with the crowd and build a personal relationship with attendees.
 * Create Live twitter walls for event
 * No complex moderation needed.
 * Customize your live view with help of various options.
 * Auto Storify view after event is over.
""",
    'depends': ['website_twitter'],
    'data': [
        'security/ir.model.access.csv',
        'views/odex25_website_twitter_wall_templates.xml',
        'views/odex25_website_twitter_wall_views.xml',
    ],
}
