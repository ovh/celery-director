const COLORS = {
  success: {
    background: "#4caf50",
    border: "#1d7521",
    hlborder: "#237d27",
  },
  error: {
    background: "#f44336",
    border: "#c7261a",
    hlborder: "#b8170b",
  },
  pending: {
    background: "#787777",
    border: "#555",
    hlborder: "#635f5f",
  },
  progress: {
    background: "#2196f3",
    border: "#0b7dda",
    hlborder: "#0961aa",
  },
};

const router = new VueRouter({
  mode: HISTORY_MODE ? "history" : "hash",
  routes: [
    {
      name: "home",
      path: "/",
    },
    {
      name: 'definitions',
      path: '/definitions'
    },
    {
      name: 'worfklow',
      path: '/:id'
    }
  ]
});

const store = new Vuex.Store({
  state: {
    definitions: [],
    workflows: [],
    workflowNames: [],
    network: null,
    selectedWorkflow: null,
    selectedTask: null,
    taskIndex: null,
    loading: true,
  },
  actions: {
    listWorkflows({ commit }) {
      axios.get(API_URL + "/workflows?with_payload=false").then((response) => {
        commit("updateWorkflows", response.data);
        commit("changeLoadingState", false);
      });
    },
    listDefinitions({
      commit
    }) {
      axios.get(API_URL + "/definitions").then((response) => {
        commit('updateDefinitions', response.data)
        commit('changeLoadingState', false)
      })
    },
    getWorkflow({ commit }, workflow_id) {
      axios.get(API_URL + "/workflows/" + workflow_id).then((response) => {
        commit("updateSelectedWorkflow", response.data);
        commit("refreshNetwork", response.data.tasks);
        commit("changeLoadingState", false);
      });
    },
    selectTask({ commit }, task) {
      commit("updateSelectedTask", task);
    },
    relaunchWorkflow({ commit, dispatch }, workflow_id) {
      axios
        .post(API_URL + "/workflows/" + workflow_id + "/relaunch")
        .then((response) => {
          dispatch("listWorkflows");
          dispatch("getWorkflow", response.data.id);
        });
    },
  },
  mutations: {
    updateWorkflows(state, workflows) {
      state.workflows = workflows;
      state.workflowNames = ["All"].concat([
        ...new Set(workflows.map((item) => item.fullname)),
      ]);
    },
    updateDefinitions(state, definitions) {
      state.definitions = definitions
    },
    updateSelectedWorkflow(state, workflow) {
      state.taskIndex = null;
      state.selectedTask = null;
      state.selectedWorkflow = workflow;
    },
    updateSelectedTask(state, task) {
      state.selectedTask = task;
    },
    refreshNetwork(state, tasks) {
      var g = new dagreD3.graphlib.Graph().setGraph({});

      for (let i = 0; i < tasks.length; i++) {
        var className = tasks[i].status;
        var html = "<div class=pointer>";
        html += "<span class=status></span>";
        html += "<span class=name>" + tasks[i].key + "</span>";
        html += "<br>";
        html += "<span class=details>" + tasks[i].status + "</span>";
        html += "</div>";

        g.setNode(tasks[i].id, {
          labelType: "html",
          label: html,
          rx: 3,
          ry: 3,
          padding: 0,
          class: className,
        });

        for (let j = 0; j < tasks[i].previous.length; j++) {
          g.setEdge(tasks[i].previous[j], tasks[i].id, {});
        }
      }

      // Set some general styles
      g.nodes().forEach(function (v) {
        var node = g.node(v);
        node.rx = node.ry = 5;
      });

      var svg = d3.select("svg"),
        inner = svg.select("g");

      // Set up zoom support
      var zoom = d3.zoom().on("zoom", function () {
        inner.attr("transform", d3.event.transform);
      });
      inner.call(zoom.transform, d3.zoomIdentity);
      svg.call(zoom);

      // Create the renderer
      var render = new dagreD3.render();
      render(inner, g);

      // Handle the click
      var nodes = inner.selectAll("g.node");
      nodes.on("click", function (task_id) {
        g.nodes().forEach(function (v) {
          if (v == task_id) {
            g.node(v).style = "fill: #f0f0f0; stroke-width: 2px; stroke: #777;";
          } else {
            g.node(v).style = "fill: white";
          }
        });

        render(inner, g);
        state.selectedTask = tasks.find((c) => c.id == task_id);
      });
    },
    changeLoadingState(state, loading) {
      state.loading = loading;
    },
  },
});

Vue.filter("formatDate", function (value) {
  if (value) {
    return moment.utc(value).local().format("YYYY-MM-DD HH:mm:ss Z");
  }
});

Vue.filter("statusColor", function (status) {
  if (status == "success") {
    return "#4caf50";
  } else if (status == "error") {
    return "#f44336";
  } else if (status == "progress") {
    return "#2196f3";
  } else {
    return "#787777";
  }
});

Vue.filter("countTasksByStatus", function (workflows, status) {
  const tasks = workflows.filter((c) => c.status === status);
  return tasks.length;
});

new Vue({
  el: "#app",
  computed: {
    headers() {
      return [
        {
          text: "ID",
          value: "id",
          align: " d-none",
        },
        {
          text: "Status",
          align: "left",
          value: "status",
          width: "14%",
          filter: (value) => {
            if (this.selectedStatus.length == 0) return true;
            return this.selectedStatus.includes(value);
          },
        },
        {
          text: "Name",
          align: "left",
          value: "fullname",
          width: "56%",
          filter: (value) => {
            if (
              !this.selectedWorkflowName ||
              this.selectedWorkflowName == "All"
            )
              return true;
            return value == this.selectedWorkflowName;
          },
        },
        {
          text: "Date",
          align: "left",
          value: "created",
          width: "30%",
        },
      ];
    },
    ...Vuex.mapState([
      "definitions",
      "workflows",
      "workflowNames",
      "selectedWorkflow",
      "selectedTask",
      "taskIndex",
      "network",
      "loading",
    ]),
  },
  store,
  router,
  vuetify: new Vuetify(),
  data: () => ({
    // navigation
    isHome: false,
    drawer: false,
    group: null,
    docLink: DOCUMENTATION_LINK,
    repoLink: REPO_LINK,
    // definitions
    multiLine: true,
    snackbar: false,
    dialog: false,
    postWorkflowResponse: "",
    dialogState: "",
    statusAlert: { success: "success", error: "error", pending: "pending" },
    isWorkflowRun: false,
    payloadValue: "",
    selectedRunningWorkflow: null,
    postWorkflowErrorJSON: "",
    // workflow (home)
    interval: null,
    tab: null,
    payloadDialog: false,
    relaunchDialog: false,
    search: "",
    selectedStatus: [],
    status: ["success", "error", "progress", "pending"],
    selectedWorkflowName: "All",
  }),
  mounted() {
    const theme = localStorage.getItem("dark_theme");
    if (theme) {
      if (theme === "true") {
        this.$vuetify.theme.dark = true;
      } else {
        this.$vuetify.theme.dark = false;
      }
    } else if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      this.$vuetify.theme.dark = true;
      localStorage.setItem("dark_theme", this.$vuetify.theme.dark.toString());
    }
  },
  methods: {
    moveUp: function () {
      window.scrollTo(0, 0);
    },
    getColor: function (status) {
      var color = {
        success: "green",
        error: "red",
        warning: "orange",
        progress: "blue",
      }[status];
      return color;
    },
    selectRow: function (item) {
      // Catch to avoid redundant navigation to current location error
      this.$router
        .push({
          name: "worfklow",
          params: {
            id: item.id,
          },
        })
        .catch(() => {});

      this.$store.dispatch("getWorkflow", item.id);
    },
    displayTask: function (task) {
      this.$store.dispatch("selectTask", task);
    },
    relaunchWorkflow: function () {
      this.$store.dispatch("relaunchWorkflow", this.selectedWorkflow.id);
      this.relaunchDialog = false;
    },
    getFlowerTaskUrl: function () {
      if (this.selectedTask) {
        return FLOWER_URL + "/task/" + this.selectedTask.id;
      }
      return "";
    },

    runButton: function (item) {
      (this.postWorkflowResponse = ""),
        (this.postWorkflowErrorJSON = ""),
        (this.payloadValue = ""),
        (this.dialog = true),
        (this.snackbar = false),
        (this.selectedRunningWorkflow = item);
    },

    runWorkflow: function () {
      this.snackbar = true;
      let payloadValueParsed;
      let payloadValueTrim = this.payloadValue.trim();
      this.dialogState = this.statusAlert.pending;
      this.isWorkflowRun = true;

      try {
        if (payloadValueTrim.length > 0) {
          payloadValueParsed = JSON.parse(payloadValueTrim);
        } else {
          payloadValueParsed = payloadValueTrim;
        }
      } catch (error) {
        this.postWorkflowErrorJSON = error;
      }

      let data = {
        project: this.selectedRunningWorkflow.project,
        name: this.selectedRunningWorkflow.name,
        payload: payloadValueTrim ? payloadValueParsed : {},
      };

      const headers = { "content-type": "application/json" };
      const urlWorkflow = API_URL + "/workflows";
      axios
        .post(urlWorkflow, data, { headers: headers })
        .then((response) => {
          this.postWorkflowResponse = response.data;
          this.dialogState = this.statusAlert.success;
        })
        .catch((error) => {
          this.postWorkflowResponse = error;
          this.dialogState = this.statusAlert.error;
        })
        .finally(
          () => (
            (this.selectedRunningWorkflow = null), (this.isWorkflowRun = false)
          )
        );
    },
  },
  watch: {
    "$vuetify.theme.dark"(newValue) {
      localStorage.setItem("dark_theme", newValue);
    },
  },
  created() {
    this.isHome = true;
    this.$store.dispatch('listDefinitions');
    this.$store.dispatch('listWorkflows');

    this.interval = setInterval(() => {
      this.$store.dispatch("listWorkflows");
    }, REFRESH_INTERVAL);

    if (this.$route.name == "definitions") {
        this.isHome = false;
    }

    let workflowID = this.$route.params.id;
    if (workflowID) {
      this.$store.dispatch("getWorkflow", workflowID);
    }
  },
  beforeDestroy() {
    clearInterval(this.interval);
  },
});
