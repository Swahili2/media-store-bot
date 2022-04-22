from plugins.database import db
from info import CUSTOM_FILE_CAPTION, BUTTON,START_MSG
from plugins.status import handle_user_status
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,ForceReply
from pyrogram import Client, filters
import re
from pyrogram.errors import UserNotParticipant
from utils import get_filter_results, get_file_details, is_subscribed
BUTTONS = {}
BOT = {}

@Client.on_message(filters.command("start"))
async def start(bot, cmd):
    usr_cmdall1 = cmd.text
    if usr_cmdall1.startswith("/start subinps"):
        await handle_user_status(bot,cmd)   
        try:
            ident, file_id = cmd.text.split("_-_-_-_")
            filedetails = await get_file_details(file_id)
            for files in filedetails:
                title = files.file_name.split('.dd#.')[1]
                f_caption=files.caption
            strg=files.file_name.split('.dd#.')[3]
            if filedetails:
                ban_status = await db.get_ban_status(cmd.from_user.id)
                if ban_status["is_banned"]:
                    if strg.lower() == 'm':
                        filez=await get_filter_results(file_id)
                        for file in reversed(filez):
                            filedetails = await get_file_details(file.file_id)
                            for files in filedetails:
                                title = files.file_name
                                f_caption=files.caption if files.caption else "🌟 @bandolako2bot"
                                await bot.send_cached_media(
                                    chat_id=cmd.from_user.id,
                                    file_id=files.file_id,
                                    caption=f_caption
                                )
                        return
                    elif strg.lower() == 's':
                        link = files.file_name.split('.dd#.')[4]
                        f_caption =f'🎬{title} \n🌟 @Bandolako2bot \n\n ***Series zetu zote zipo google drive,Kama huwezi kufungua link tutumie email yako @hrm45 inbox tukuunge***'
                        await bot.send_photo(
                            chat_id=cmd.from_user.id,
                            photo=files.mime_type,
                            caption=f_caption,
                            reply_markup=InlineKeyboardMarkup(InlineKeyboardButton("🔗 GOOGLE LINK",url= link))
                        )
                        return
                     
                else:
                    await bot.send_message(
                        chat_id=cmd.from_user.id,
                        text=f"Samahani **{cmd.from_user.first_name}** nmeshindwa kukuruhusu kendelea kwa sababu muv au sizon uliochagua ni za kulipia\n Tafadhal chagua nchi uliopo kuweza kulipia kifurushi",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("🇹🇿 TANZANIA", callback_data = "tanzania"),
                                    InlineKeyboardButton("🇰🇪 KENYA",callback_data ="kenya" )
                                ]
                            ]
                        )
                    )
                    return
        #except Exception as err:
            #await cmd.reply_text(f"Something went wrong!\n\n**Error:** `{err}`")
    elif cmd.chat.type == 'private':
        await cmd.reply_text(
            START_MSG,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✈️ About", callback_data="about"),
                        InlineKeyboardButton("👨‍👨‍👧‍👧Group zetu", switch_inline_query_current_chat='')
                    ],
                    [
                        InlineKeyboardButton("🩸 NI ADD KWENYE GROUP 🩸",url='http://t.me/bandolako2021bot?startgroup=true')
                    ]
                ]
                )
            )

Client.on_message(filters.text & filters.private & filters.incoming)
async def filter(client, message):
    await handle_user_status(client,message)
    if message.text.startswith("/"):
        return
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return
   
@Client.on_message(filters.text & filters.group & filters.incoming)
async def group(client, message):
    await handle_user_status(client,message)
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return
    if 2 < len(message.text) < 50:    
        btn = []
        search = message.text
        nyva=BOT.get("username")
        if not nyva:
            botusername=await client.get_me()
            nyva=botusername.username
            BOT["username"]=nyva
        files = await get_filter_results(query=search)
        if files:
            for file in files:
                title = file.file_name.split('.dd#.')[1]
                file_id = file.file_id
                filename = f"[{get_size(file.file_size)}] {title}"
                btn.append(
                    [InlineKeyboardButton(text=f"{filename}", url=f"https://telegram.dog/{nyva}?start=subinps_-_-_-_{file_id}##{message.chat.id}")]
                )
            await message.reply_text(f"<b>Bonyeza kitufe <b>(🔍Majibu ya Database : {len(btn)})</b> Kisha subir kidogo,kisha chagua unachokipenda.\n\n💥Kwa urahisi zaidi kutafta chochote anza na aina kama ni  movie, series ,(audio ,video) kwa music , vichekesho kisha acha nafasi tuma jina la  kitu unachotaka mfano video jeje au audio jeje au movie extraction au series soz­</b>", reply_markup=get_reply_makup(search,len(btn)))
        else:
            return
        if not btn:
            return
def get_reply_makup(query,totol):
    buttons = [
        [
            InlineKeyboardButton('🔍Majibu ya Database: '+ str(totol), switch_inline_query_current_chat=query),
        ]
        ]
    return InlineKeyboardMarkup(buttons)
              
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    clicked = query.from_user.id
    try:
        typed = query.message.reply_to_message.from_user.id
    except:
        typed = query.from_user.id
        pass
    if (clicked == typed):
        if query.data == "about":
            await query.answer('Mimi ni coder naitwa hrm45 nmesoma mtandaoni kwa kujifunza doc tofauti tofauti kama kuna makosa tujulishe tuboreshe huduma zetu',show_alert=True)
            
        elif query.data == "close":
            try:
                await query.message.reply_to_message.delete()
                await query.message.delete()
            except:
                await query.message.delete()
                
        elif query.data == "kenya":
            await query.answer()
            mkv = await client.ask(text = " Samahani sana wateja wetu wa Kenya bado hatuja weka utaratibu mzuri.\n  hivi karibun tutaweka mfumo mzuri ili muweze kupata huduma zetu", chat_id = query.from_user.id)
        
        elif query.data == "tanzania":
            await query.answer()
            await client.send_message(chat_id = query.from_user.id,text="🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿\n** VIFURUSHI VYA SWAHILI GROUP** \n🔴 wiki 1(07 days) ➡️ 2000/= \n\n🟠 wiki 2(14 days) ➡️ 3000/= \n\n🟡 wiki 3(21 days) ➡️ 4000/= \n\n🟢 mwezi (30 days) ➡️ 5000/= \n\n↘️Lipa kwenda **0624667219** halopesa:Ukishafanya malipo bonyeza button nmeshafanya malipo\n **__KARIBUN SANA SWAHILI GROUP__**",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔴 Nmeshafanya malipo", callback_data="malipo")]]))
        
        elif query.data == "malipo":
            await query.answer()
            mkv = await client.ask(text='🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿\nTuma screenshot ya malipo yako kisha subir kidogo wasimamiz wangu wahakiki muamala wako',chat_id = query.from_user.id,reply_markup=ForceReply())
            if mkv.photo:
                await client.send_message(chat_id = query.from_user.id,text='🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿\ntumepokea screenshot ngoja tuihakiki tutakupa majibu tukimaliza')
                await client.send_photo(
                            chat_id=859704527,
                            photo= mkv.photo.file_id,
                            caption =f'id = {query.from_user.id}\n Name : {query.from_user.first_name}' )
            else:
                await client.send_message(chat_id = query.from_user.id,text = " Nmelazimika kukurudisha hapa kwa sababu umetuma ujumbe sio sahihi\n🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿🇹🇿\n** VIFURUSHI VYA SWAHILI GROUP** \n🔴 wiki 1(07 days) ➡️ 2000/= \n\n🟠 wiki 2(14 days) ➡️ 3000/= \n\n🟡 wiki 3(21 days) ➡️ 4000/= \n\n🟢 mwezi (30 days) ➡️ 5000/= \n\n↘️Lipa kwenda **0624667219** halopesa:Ukishafanya malipo bonyeza button nmeshafanya malipo\n **__KARIBUN SANA SWAHILI GROUP__**",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔴 Nmeshafanya malipo", callback_data="malipo")]]))
