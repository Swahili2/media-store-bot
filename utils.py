import re
import base64
import logging
from struct import pack
from plugins.database import db
from telegraph import upload_file
from pyrogram.errors import UserNotParticipant
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from marshmallow.exceptions import ValidationError
import os
import PTN
import requests
import json
from info import DB2, COLLECTION_NAME, USE_CAPTION_FILTER, AUTH_CHANNEL, API_KEY

COLLECTION_NAME_2="groups"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

instance = Instance.from_db(DB2)
imdb=Instance.from_db(DB2)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        collection_name = COLLECTION_NAME

@imdb.register
class Group(Document):
    id = fields.IntField(attribute='_id')
    user_id= fields.IntField(required=True)
    title = fields.StrField(required=True)
    link_inv = fields.StrField(required=True)
    total_m = fields.IntField(required=True)
    thumb = fields.StrField(allow_none=True)
    amount = fields.IntField(allow_none=True)
    phone_no = fields.StrField(allow_none=True)
    class Meta:
        collection_name = COLLECTION_NAME_2

async def save_group(id, usr,tit, link,tot , thu,amt,pn):
    try:
        data = Group(
            id = id,
            user_id= usr,
            title = tit,
            link_inv = link,
            total_m = tot ,
            thumb =thu,
            amount = amt,
            phone_no = pn
        )
    except ValidationError:
        logger.exception('Error occurred while saving group in database')
    else:
        try:
            await data.commit()
        except DuplicateKeyError:
            logger.warning("already saved in database")
        else:
            logger.info("group is saved in database")

async def save_file(media):
    """Save file in database"""

    # TODO: Find better way to get same file_id for same media to avoid duplicates
    file_ref= media.file_ref
    file_id = media.file_id
    if media.file_type != "photo":
        file_id, file_ref = unpack_new_file_id(media.file_id)

    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=media.file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(media.file_name + " is already saved in database")
            return 'file exist', file_id
        else:
            logger.info(media.file_name + " is saved in database")
            return 'file sent', file_id 

async def get_search_results(query, file_type=None, max_results=10, offset=0):
    """For given query return (results, next_offset)"""

    query = query.strip()
    if not query:
        query = 'dd# x'
    query = query.lower()
    if query=='movie':
        query='movie x'
    if ' ' not in query:
        raw_pattern = r'\b' + query + r'.*'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(filter)
    # Sort by recent
    cursor.sort('$natural', -1)
    # Slice files according to offset and max results
    cursor.skip(offset).limit(max_results)
    # Get list of files
    files = await cursor.to_list(length=max_results)

    return files, next_offset


async def get_filter_results(query):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'\b' + query + r'.*'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []
    filter = {'file_name': regex}
    total_results = await Media.count_documents(filter)
    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    files = await cursor.to_list(length=int(total_results))
    return files

async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails


async def is_group_exist(query):
    filter = {'id': query}
    cursor = Group.find(filter)
    groupdetails = await cursor.to_list(length=1)
    return groupdetails


async def is_subscribed(bot, query):
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if not user.status == 'kicked':
            return True

    return False
async def get_group_filters(query , max_results=10, offset=0):
    """For given query return (results, next_offset)"""

    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'\b' + query + r'.*'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    filter = {'title': regex}

    total_results = await Group.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Group.find(filter)
    # Sort by recent
    cursor.sort('$natural', -1)
    # Slice files according to offset and max results
    cursor.skip(offset).limit(max_results)
    # Get list of files
    files = await cursor.to_list(length=max_results)

    return files, next_offset

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
async def upload_group(client, thumb,message):
  img_path = (f"./DOWNLOADS/{message.from_user.id}.jpg")
  if thumb:
    img_path = await client.download_media(message=thumb.big_file_id, file_name=img_path)
  else:
    return None
  try:
    tlink = upload_file(img_path)
  except:
    await msg.edit_text("`Something went wrong`")
    return None
  else: 
    os.remove(img_path)
  link2= f"https://telegra.ph{tlink[0]}"
  return link2
async def upload_photo(client, message):
  msg = await message.reply_text("`Tʀʏɪɴɢ Tᴏ Dᴏᴡɴʟᴏᴀᴅ`")
  id3 = message.photo.file_id
  userid = f'{id3}{message.photo.file_size}'
  img_path = (f"./DOWNLOADS/{userid}.jpg")
  img_path = await client.download_media(message=message, file_name=img_path)
  await msg.edit_text("`Tʀʏɪɴɢ Tᴏ Uᴘʟᴏᴀᴅ.....`")
  try:
    tlink = upload_file(img_path)
  except:
    await msg.edit_text("`Something went wrong`") 
  else:
    await msg.edit_text(f"https://telegra.ph{tlink[0]}")     
    os.remove(img_path)
  link2= f"https://telegra.ph{tlink[0]}"
  id2=(tlink[0].split("/")[-1]).split(".")[0]
  return f'{id2}{message.photo.file_size}',id3,link2

def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])
