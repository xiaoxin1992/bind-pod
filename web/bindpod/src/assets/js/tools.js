import ElementUI from 'element-ui';

export default {
    notify(msg, title, type, pos='top-right') {
        ElementUI.Notification({
            type: type,
            title: title,
            position: pos,
            message: msg,
            duration: 2000,
            offset: 60
        })
    }
}
