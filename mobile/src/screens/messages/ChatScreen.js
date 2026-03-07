/**
 * ChatScreen — Conversation en temps réel
 */
import React, {useState, useEffect, useRef} from 'react';
import {
  View, Text, StyleSheet, FlatList, TextInput,
  TouchableOpacity, KeyboardAvoidingView, Platform,
} from 'react-native';
import api from '../../services/api';
import {useAuth} from '../../contexts/AuthContext';

const Bubble = ({msg, isMe}) => (
  <View style={[styles.bubble, isMe ? styles.bubbleMe : styles.bubbleOther]}>
    <Text style={[styles.bubbleText, isMe && styles.bubbleTextMe]}>{msg.content}</Text>
    <Text style={[styles.bubbleTime, isMe && {color: '#bfdbfe'}]}>
      {new Date(msg.created_at).toLocaleTimeString('fr-MA', {hour: '2-digit', minute: '2-digit'})}
    </Text>
  </View>
);

const ChatScreen = ({route}) => {
  const {conversation} = route.params;
  const {user} = useAuth();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const listRef = useRef(null);

  const fetchMessages = async () => {
    try {
      const res = await api.get(`/messages/conversations/${conversation.id}/messages`);
      setMessages((res.data?.messages || res.data || []).reverse());
    } catch (_) {}
  };

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000); // polling toutes les 5s
    return () => clearInterval(interval);
  }, []);

  const sendMessage = async () => {
    if (!text.trim()) return;
    const content = text.trim();
    setText('');
    try {
      await api.post(`/messages/conversations/${conversation.id}/messages`, {content});
      fetchMessages();
    } catch (_) {}
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={90}>
      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(i) => String(i.id)}
        renderItem={({item}) => (
          <Bubble msg={item} isMe={item.sender_id === user?.id} />
        )}
        onContentSizeChange={() => listRef.current?.scrollToEnd({animated: true})}
        contentContainerStyle={{padding: 12}}
      />
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={text}
          onChangeText={setText}
          placeholder="Écrire un message…"
          multiline
          maxLength={1000}
        />
        <TouchableOpacity style={styles.sendBtn} onPress={sendMessage}>
          <Text style={styles.sendIcon}>➤</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc'},
  bubble: {maxWidth: '78%', marginBottom: 10, padding: 12, borderRadius: 16},
  bubbleMe: {alignSelf: 'flex-end', backgroundColor: '#3b82f6', borderBottomRightRadius: 4},
  bubbleOther: {alignSelf: 'flex-start', backgroundColor: '#fff', elevation: 1, borderBottomLeftRadius: 4},
  bubbleText: {fontSize: 15, color: '#1e293b'},
  bubbleTextMe: {color: '#fff'},
  bubbleTime: {fontSize: 10, color: '#64748b', marginTop: 4, alignSelf: 'flex-end'},
  inputRow: {flexDirection: 'row', padding: 12, backgroundColor: '#fff', alignItems: 'flex-end', borderTopWidth: 1, borderTopColor: '#e2e8f0'},
  input: {flex: 1, backgroundColor: '#f1f5f9', borderRadius: 20, paddingHorizontal: 16, paddingVertical: 10, fontSize: 15, maxHeight: 120},
  sendBtn: {marginLeft: 8, backgroundColor: '#3b82f6', borderRadius: 22, width: 44, height: 44, alignItems: 'center', justifyContent: 'center'},
  sendIcon: {color: '#fff', fontSize: 18},
});

export default ChatScreen;
