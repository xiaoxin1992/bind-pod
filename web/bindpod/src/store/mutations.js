export default {
    saveUserName(state, username) {
        state.username = username.username;
        state.display_name = username.display_name;
        state.is_superuser = username.is_superuser;
    },
}
