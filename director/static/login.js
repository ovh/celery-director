new Vue({
  el: '#login',
  vuetify: new Vuetify({
    theme: {
      dark: DARK_THEME,
    },
  }),
  data: () => ({
    valid: true,
    auth: {
      username: '',
      password: ''
    },
    returnUrl: '',
    rules: {
      username: [
        username => !!username || 'Username is required',
      ],
      password: [
        password => !!password || 'Password is required'
      ],
    },
    error: ''
  }),
  methods: {
    checkCredentials: function () {
      axios({
        method: 'get',
        url: API_URL + '/check_credentials',
        auth: this.auth
      }).then((response) => {
        if (response.status === 204) {
          localStorage.setItem('user', JSON.stringify(this.auth));
          window.location.replace(this.returnUrl);
          return;
        }

      }).catch(() => {
        this.error = 'Invalid username or password';
      });
    },
    login: function () {
      if (!this.$refs.form.validate()) {
        return;
      }

      this.checkCredentials();
    }
  },
  created() {
    var urlParams = new URLSearchParams(window.location.search);
    this.returnUrl = urlParams.get('returnUrl') || '/';
  }
});
