const COLORS = {
  'success': {
    'background': '#4caf50',
    'border': '#1d7521',
    'hlborder': '#237d27'
  },
  'error': {
    'background': '#f44336',
    'border': '#c7261a',
    'hlborder': '#b8170b'
  },
  'pending': {
    'background': '#787777',
    'border': '#555',
    'hlborder': '#635f5f'
  }
};

function getNode(task) {
  return {
    id: task.id,
    label: task.key,
    shape: 'box',
    borderWidth: 1,
    color: {
      border: COLORS[task.status]['border'],
      background: COLORS[task.status]['background'],
      highlight: {
        background: COLORS[task.status]['background'],
        border: COLORS[task.status]['hlborder'],
      }
    },
    font: {
      face: 'arial',
      align: 'center',
      color: '#fff',
      strokeWidth: 0,
      strokeColor: '#ffffff',
    }
  };
}

const store = new Vuex.Store({
	state: {
    workflows: [],
    network: null,
    selectedWorkflow: null,
    selectedTask: null,
    taskIndex: null,
    loading: true
  },
  actions: {
    listWorkflows({commit}) {
      axios.get(API_URL + "/workflows").then((response) => {
        commit('updateWorkflows', response.data)
        commit('changeLoadingState', false)
    	})
    },
    getWorkflow({commit}, workflow_id) {
      axios.get(API_URL + "/workflows/" + workflow_id).then((response) => {
        commit('updateSelectedWorkflow', response.data)
        commit('refreshNetwork', response.data.tasks)
        commit('changeLoadingState', false)
    	})
    },
    selectTask({commit}, task) {
      commit('updateSelectedTask', task)
    }
  },
  mutations: {
    updateWorkflows(state, workflows) {
      state.workflows = workflows
    },
    updateSelectedWorkflow(state, workflow) {
      state.taskIndex = null
      state.selectedWorkflow = workflow
    },
    updateSelectedTask(state, task) {
      state.selectedTask = task
    },
    refreshNetwork(state, tasks) {
      let nodes = [];
      let edges = [];
    
      for (let i = 0; i < tasks.length; i++) {
        nodes.push(getNode(tasks[i]));

        for (let j=0; j<tasks[i].previous.length; j++) {
          edges.push({
            'to': tasks[i].id,
            'from': tasks[i].previous[j],
            'color': {
              'color': '#3c4652',
              'highlight':'#3c4652',
            },
            'arrows': 'to',
            'physics': false, 'smooth': {'type': 'cubicBezier'}
          });
        }
      }

      container = document.getElementById('network')
      let data = {nodes:  nodes, edges: edges};
      let options = {
        nodes: {
          margin: 10
        },
        layout: {
          hierarchical: {
            direction: "UD",
            sortMethod: "directed"
          }
        },
        edges: {
          arrows: "to"
        },
      };
      state.network = new vis.Network(container, data, options);
      state.network.on( 'click', function(properties) {
        if ( properties.nodes.length > 0 ) {
          let taskID = properties.nodes[0];
          state.taskIndex = tasks.findIndex(c => c.id == taskID);
        }
      });
    },
    changeLoadingState(state, loading) {
    	state.loading = loading
    }
  }
});


Vue.filter('formatDate', function(value) {
  if (value) {
    return moment(String(value)).format('MMM DD, HH:mm:ss')
  }
});

Vue.filter('statusColor', function(status) {
  if ( status == 'success' ) {
    return '#4caf50';
  } else if ( status == 'error' ) {
    return '#f44336';
  } else {
    return '#787777';
  }
});

Vue.filter('countTasksByStatus', function(workflows, status) {
    const tasks = workflows.filter(c => c.status === status);
    return tasks.length;
});

new Vue({
    el: '#app',
    computed: Vuex.mapState(['workflows', 'selectedWorkflow', 'selectedTask', 'taskIndex', 'network', 'loading', 'headers']),
    store,
    vuetify: new Vuetify({
      theme: {
        dark: DARK_THEME,
      },
    }),
    data: () => ({
      drawer: null,
      dialog: false,
      dialogTask: false,
      search: '',
      headers: [
        {
          text: 'Name',
          align: 'left',
          value: 'fullname',
        },
        { text: 'Date', value: 'created' },
        { text: 'Status', value: 'status' },
      ],
    }),
    methods: {
      getColor: function (status) {
        var color = {
          'success': 'green',
          'error': 'red',
          'warning': 'orange'
        }[status];
        return color;
      },
      selectRow: function (item) {
        let prevItem = this.workflows.find(c => c.isSelected);
        if (prevItem) this.$delete(prevItem, 'isSelected');
        this.$set(item, "isSelected", true)
        this.$store.dispatch('getWorkflow', item.id)
      },
      displayTask: function(task) {
        this.$store.dispatch('selectTask', task);
        this.dialogTask = true;
      },
      getFlowerTaskUrl: function() {
        return FLOWER_URL + "/task/" + this.selectedTask.id;
      }
    },
    created() {
      this.$store.dispatch('listWorkflows')
    }
  });
