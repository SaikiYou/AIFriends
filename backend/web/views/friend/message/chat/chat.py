import json

from django.http import StreamingHttpResponse
from langchain_core.messages import HumanMessage, BaseMessageChunk, SystemMessage

from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Friend, Message,SystemPrompt
from web.views.friend.message.chat.graph import ChatGraph
from web.views.friend.message.memory.update import update_memory


class SSERenderer(BaseRenderer):     #渲染器
    media_type = 'text/event-stream'
    format = 'txt'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

def add_system_prompt(state, friend):  #添加系统提示词
    msgs = state['messages']  #读取之前已有的信息
    system_prompts = SystemPrompt.objects.filter(title="回复").order_by('order_number') #将回复模块按照order_number排序
    prompt = ''
    for sp in system_prompts:
        prompt += sp.prompts  #连接起来
    prompt += f'\n【角色性格】\n{friend.character.profile}\n'
    prompt += f'【长期记忆】\n{friend.memory}\n'
    return {'messages': [SystemMessage(content=prompt)] + msgs}  #手动追加

def add_recent_message(state,friend):#近期对话
    msgs = state['messages']
    message_raw = list(Message.objects.filter(friend=friend).order_by('-id')[:10])#近十轮对话,因为是从新到旧排列，需要翻转对话顺序，用list包裹
    messages = []
    for m in message_raw:
        messages.append(HumanMessage(m.user_message))
        from langchain_core.messages import AIMessage
        messages.append(AIMessage(m.output))
    return {'messages':msgs[:1] + messages + msgs[-1:]} #十轮对话加在系统提示词和用户对话之间



class MessageChatView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [SSERenderer]

    def post(self, request):
        friend_id = request.data.get('friend_id')
        message =  request.data.get('message','').strip()
        if not message:
            return Response({
                'result': '请输入内容'
            })
        friend = Friend.objects.filter(pk=friend_id, me__user=request.user)
        if not friend.exists():
            return Response({
                'result': '好友不存在'
            })
        friend = friend.first()
        app = ChatGraph.create_app()

        inputs = {
            'messages': [HumanMessage(message)]
        }
        inputs = add_system_prompt(inputs, friend)
        inputs = add_recent_message(inputs, friend)

        def event_stream():
            final_output =''
            final_usage = {}
            for msg, metadata in app.stream(inputs, stream_mode="messages"):
                if isinstance(msg, BaseMessageChunk):
                    if msg.content:
                        final_output += msg.content
                        yield f"data: {json.dumps({'content': msg.content}, ensure_ascii=False)}\n\n"
                    if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                        final_usage = msg.usage_metadata
            yield "data: [DONE]\n\n"
            input_tokens = final_usage.get('input_tokens', 0)
            output_tokens = final_usage.get('output_tokens', 0)
            total_tokens = final_usage.get('total_tokens', 0)
            Message.objects.create(
                friend = friend,
                user_message = message[:500],
                input = json.dumps(
                    [m.model_dump() for m in inputs['messages']],
                    ensure_ascii=False,
                )[:10000],
                output=final_output[:500],
                input_tokens = input_tokens,
                output_tokens = output_tokens,
                total_tokens = total_tokens,
            )

            if Message.objects.filter(friend=friend).count() % 1 == 0:
                update_memory(friend)


        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response
