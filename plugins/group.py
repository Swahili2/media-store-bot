from plugins.database import db
from info import CUSTOM_FILE_CAPTION, BUTTON,START_MSG
from plugins.status import handle_user_status
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,ReplyKeyboardForceReply
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
                title = files.file_name
                size=get_size(files.file_size)
                f_caption=files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                    except Exception as e:
                        print(e)
                        f_caption=f_caption
            strg=files.file_name.split('.dd#.')[3]
            strgs = strg.split('.')[1]
            strg2 = strg.split('.')[0]
            link = files.file_name.split('.dd#.')[4]
            if filedetails:
                ban_status = await db.get_ban_status(cmd.from_user.id)
                if strgs.lower() == 'f' or ban_status["is_banned"]:
                    if strg2.lower() == 'm':
                        f_caption=f'🎬title \n🌟 @Bandolako2bot \n\n ***bonyeza download kuzidownload hapa telegram au google kudownload kupitia google drive***\n *usisahau mda wowote kuweka email kwa kutuma neno wekaemail kisha email yako mfano wekaemail hramamohamed@gmail.com*'
                        buttns = [
                                [
                                    InlineKeyboardButton("📤 DOWNLOAD",callback_data=f"subinps.dd#.{files.file_id}")
                          
                                ],
                                [
                                    InlineKeyboardButton("🔗 GOOGLE LINK",url= link)
                                ]
                            ]
                        await bot.send_photo(
                            chat_id=cmd.from_user.id,
                            photo=files.mime_type,
                            caption=f_caption,
                            reply_markup=InlineKeyboardMarkup(buttns)
                        )
                    elif strg2.lower() == 's':
                        filef=await get_filter_results(file_id)
                        f_caption =f'🎬title \n🌟 @Bandolako2bot \n\n ***Bonyeza google link kudownload kupitia google drive na bonyeza season episode range(s01()1-n) kudownload episode husika hapa telegram tunaanza na latest episodes kurud mpaka ya mwanzo*** \n\n *kama hujaunga email tuma neno wekaemail kisha email yako mfano wekaemail hramamohamed@gmail.com*'
                        output = []
                        output.append(InlineKeyboardButton("🔗 GOOGLE LINK",url= link))
                        for x in filef:
                            i= x.file_name.split('.dd#.')[2]
                            a,b= i.split('.d#.')
                            l1,l2= a.split('@.')
                            dataa=InlineKeyboardButton(f"{b}",callback_data=f"subinps.dd#.{l1} {l2}" )
                            if dataa not in output:
                                output.append(dataa)
                        buttons=list(split_list(output,2))
                        if len(buttons) > 10: 
                            btns = list(split_list(buttons, 10)) 
                            keyword = f"{message.chat.id}-{message.message_id}"
                            BUTTONS[keyword] = {
                               "total" : len(btns),
                               "buttons" : btns
                            }
                        else:
                            buttons = buttons
                            buttons.append(
                                [InlineKeyboardButton(text="📃 Pages 1/1",callback_data="pages")]
                            )
                            if BUTTON:
                                buttons.append([InlineKeyboardButton(text="Close ❌",callback_data="close")])
                            await bot.send_photo(
                                chat_id=cmd.from_user.id,
                                photo=files.mime_type,
                                caption=f_caption,
                                reply_markup=InlineKeyboardMarkup(buttons)
                            )
                            return

                        data = BUTTONS[keyword]
                        buttons = data['buttons'][0].copy()

                        buttons.append(
                            [InlineKeyboardButton(text="NEXT ⏩",callback_data=f"next_0_{keyword}")]
                        )    
                        buttons.append(
                            [InlineKeyboardButton(text=f"📃 Pages 1/{data['total']}",callback_data="pages")]
                        )
                        if BUTTON:
                            buttons.append([InlineKeyboardButton(text="Close ❌",callback_data="close")])
     
                        await bot.send_photo(
                            chat_id=cmd.from_user.id,
                            photo=files.mime_type,
                            caption=f_caption,
                            reply_markup=InlineKeyboardMarkup(buttons)
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
        except Exception as err:
            await cmd.reply_text(f"Something went wrong!\n\n**Error:** `{err}`")
    else:
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
    
   
def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]          



@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    clicked = query.from_user.id
    try:
        typed = query.message.reply_to_message.from_user.id
    except:
        typed = query.from_user.id
        pass
    if (clicked == typed):

        if query.data.startswith("next"):
            ident, index, keyword = query.data.split("_")
            try:
                data = BUTTONS[keyword]
            except KeyError:
                await query.answer("You are using this for one of my old message, please send the request again.",show_alert=True)
                return

            if int(index) == int(data["total"]) - 2:
                buttons = data['buttons'][int(index)+1].copy()

                buttons.append(
                    [InlineKeyboardButton("⏪ BACK", callback_data=f"back_{int(index)+1}_{keyword}")]
                )
                buttons.append(
                    [InlineKeyboardButton(f"📃 Pages {int(index)+2}/{data['total']}", callback_data="pages")]
                )
                if BUTTON:
                    buttons.append([InlineKeyboardButton(text="Close ❌",callback_data="close")])

                await query.edit_message_reply_markup( 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
            else:
                buttons = data['buttons'][int(index)+1].copy()

                buttons.append(
                    [InlineKeyboardButton("⏪ BACK", callback_data=f"back_{int(index)+1}_{keyword}"),InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{int(index)+1}_{keyword}")]
                )
                buttons.append(
                    [InlineKeyboardButton(f"📃 Pages {int(index)+2}/{data['total']}", callback_data="pages")]
                )
                if BUTTON:
                    buttons.append([InlineKeyboardButton(text="Close ❌",callback_data="close")])

                await query.edit_message_reply_markup( 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return


        elif query.data.startswith("back"):
            ident, index, keyword = query.data.split("_")
            try:
                data = BUTTONS[keyword]
            except KeyError:
                await query.answer("You are using this for one of my old message, please send the request again.",show_alert=True)
                return

            if int(index) == 1:
                buttons = data['buttons'][int(index)-1].copy()

                buttons.append(
                    [InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{int(index)-1}_{keyword}")]
                )
                buttons.append(
                    [InlineKeyboardButton(f"📃 Pages {int(index)}/{data['total']}", callback_data="pages")]
                )
                if BUTTON:
                    buttons.append([InlineKeyboardButton(text="Close ❌",callback_data="close")])

                await query.edit_message_reply_markup( 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return   
            else:
                buttons = data['buttons'][int(index)-1].copy()

                buttons.append(
                    [InlineKeyboardButton("⏪ BACK", callback_data=f"back_{int(index)-1}_{keyword}"),InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{int(index)-1}_{keyword}")]
                )
                buttons.append(
                    [InlineKeyboardButton(f"📃 Pages {int(index)}/{data['total']}", callback_data="pages")]
                )
                if BUTTON:
                    buttons.append([InlineKeyboardButton(text="Close ❌",callback_data="close")])

                await query.edit_message_reply_markup( 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
        elif query.data == "about":
            await query.answer('Mimi ni coder naitwa hrm45 nmesoma mtandaoni kwa kujifunza doc tofauti tofauti kama kuna makosa tujulishe tuboreshe',show_alert=True)
            
        elif query.data == "pages":
            await query.answer()
        elif query.data == "close":
            try:
                await query.message.reply_to_message.delete()
                await query.message.delete()
            except:
                await query.message.delete()
                
        elif query.data.startswith("subinps"):
            ident, file_id = query.data.split(".dd#.")
            filez=await get_filter_results(file_id)
            for file in reversed(filez):
                filedetails = await get_file_details(file.file_id)
                for files in filedetails:
                    title = files.file_name
                    size=get_size(files.file_size)
                    f_caption=f"{files.caption}\n🌟 @bandolako2bot" if files.caption else "🌟 @bandolako2bot"
                    if CUSTOM_FILE_CAPTION:
                        try:
                            f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                        except Exception as e:
                            print(e)
                            f_caption=f_caption
                    await query.answer()
                    await client.send_cached_media(
                        chat_id=query.from_user.id,
                        file_id=file.file_id,
                        caption=f_caption
                    )
        elif query.data == "kenya":
            mkv = await client.ask(text = " Samahani sana wateja wetu wa Kenya bado hatuja weka utaratibu mzuri.\n  hivi karibun tutaweka mfumo mzuri ili muweze kupata huduma zetu", chat_id = query.from_user.id ,reply_markup=ReplyKeyboardForceReply())
        
        elif query.data == "tanzania":
            mkv = await client.ask(text="** VIFURUSHI VYA SWAHILI GROUP** \n wiki 1(07 days) ➡️ 2000/= \n wiki 2(14 days) ➡️ 3000/= \n wiki 3(21 days) ➡️ 4000/= \n mwezi (30 days) ➡️ 5000/= \n\n Lipa kwenda **0624667219** halopesa:Ukishafanya malipo tuma screenshot ya muamala hapa kwenye hii bot .\n\n Ukimaliza subir kidogo ntakutaarifu endapo msimamiz wangu atamaliza kuhakiki muamala wako..\nPia kila muamala utakao lipia ofa zipo unaeza kuongezewa siku(1,2,3---)\n **__KARIBUN SANA SWAHILI GROUP__**", chat_id = query.from_user.id)
        
