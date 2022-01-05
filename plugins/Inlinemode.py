import logging
from plugins. database import db
from pyrogram import Client, emoji, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument,InlineQueryResultPhoto,InputTextMessageContent,InlineQueryResultArticle


from utils import get_search_results, is_subscribed, get_size ,get_group_filters
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

BOT = {}
@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for given inline query"""
    if query.chat_type =="group" or query.chat_type=="supergroup":
    
        nyva=BOT.get("username")
    
        if not nyva:
            botusername=await bot.get_me()
            nyva=botusername.username
            BOT["username"]=nyva
        if AUTH_CHANNEL and not await is_subscribed(bot, query):
            await query.answer(results=[],
                               cache_time=0,
                               switch_pm_text='You have to subscribe my channel to use the bot',
                               switch_pm_parameter="subscribe")
            return

        results = []
        if '|' in query.query:
            string, file_type = query.query.split('|', maxsplit=1)
            string = string.strip()
            file_type = file_type.strip().lower()
        else:
            string = query.query.strip()
            file_type = None

        offset = int(query.offset or 0)
        files, next_offset = await get_search_results(string,
                                                  file_type=file_type,
                                                  max_results=10,
                                                  offset=offset)

        for file in files:
            title = file.file_name.split('.dd#.')[1]
            descp = file.file_name.split('.dd#.')[0]
            id2 = file.file_name.split('.dd#.')[2]
            size=get_size(file.file_size)
            f_caption=file.caption
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                except Exception as e:
                    print(e)
                f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            if id2=='x':
                if file.file_type != "photo":
                    reply_markup=get_reply_markup(string,file.file_id,nyva)
                    results.append(
                        InlineQueryResultCachedDocument(
                            title=title,
                            file_id=file.file_id,
                            caption=f_caption,
                            description=f'{descp}'))
                else:
                    reply_markup=get_reply_markup(string,file.file_id,nyva)
                    results.append(InlineQueryResultPhoto(
                            photo_url = file.file_ref,
                            title=title,
                            description= descp,
                            caption=f_caption,
                            reply_markup=reply_markup))      
        if results:
            title =f"Mpendwa {query.from_user.first_name}"
            results. append(InlineQueryResultArticle(
                    title=title,
                    input_message_content=InputTextMessageContent(message_text = f"Mpendwa **{query. from_user.first_name}**\nKama movie yako haipo hakikisha kwenye orodha zetu kwa kutuma neno orodha au kwa uharaka zaidi tuma neno movie au series n.k ikifuatiwa na aa kwa muv au series n.k zinazoanziwa na a au bb zinazoanziwa na b ,Ukikosa kabisa tutumie hilo jina la muv au series au chochote kile kilichokesekana kwenye huduma zetu \n[BONYEZA HAPA KUTUMA](https://t.me/Swahili_msaadabot)", disable_web_page_preview = True),
                    description=f'Hapa ndiyo mwisho wa  matokeo yetu kutoka kwenye database\nBonyeza hapa kama haipo kupata maelezo zaidi')
                )
            try:
                await query.answer(results=results,
                               is_personal = True,
                               cache_time=cache_time,
                               next_offset=str(next_offset))
            except Exception as e:
                logging.exception(str(e))
                await query.answer(results=[], is_personal=True,
                               cache_time=cache_time,
                               switch_pm_text=str(e)[:63],
                               switch_pm_parameter="error")
        else:

            switch_pm_text = f'{emoji.CROSS_MARK} No results'
            if string:
                switch_pm_text += f' for "{string}"'

            await query.answer(results=[],
                           is_personal = True,
                           cache_time=cache_time,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="okay")
    else:
        result = []
        string = query.query.strip()
        offset = int(query.offset or 0)
        files ,next_offset= await get_group_filters(string,max_results=10,offset=offset)
        for file in files:
             ttl=await bot.get_users(file.user_id)
             title = f"🎁🎁 {file.title} 🎁🎁"
             text1= f"👨‍👨‍👧‍👧 Group name:**{file.title}**\n\n👨‍👧‍👧 Total_members : **{file.total_m}*"\n\n🙍🙍‍♀ Admin name:**{ttl.first_name}**\n\nJiunge sasa uweze kupata muv,sizon zisizotafsiriwa na ambazo hazijatafsiriwa,miziki,vichekesho n.k kupitia swahili robot\nBonyeza 👨‍👧‍👧 join group kujiunga"
             result.append(InlineQueryResultArticle(
                        title=title,
                        input_message_content=InputTextMessageContent(message_text = text1, disable_web_page_preview = True),
                        description=f'total members : {file.total_m} \nGusa hapa kujoin group kupata movie series miziki nakadhalika',
                        thumb_url=file["thumb"],
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('👨‍👧‍👧 join group', url=file["link_inv"])]])
                    ))
        await query.answer(results=result,
                        is_personal = True,
                        cache_time=cache_time,
                        next_offset=str(next_offset)
                    )

def get_reply_markup(query, file_id, nyva):
    buttons = [
        [
            InlineKeyboardButton('📤 Download', url=f"https://telegram.dog/{nyva}?start=subinps_-_-_-_{file_id}")
        ]
        ]
    return InlineKeyboardMarkup(buttons)
