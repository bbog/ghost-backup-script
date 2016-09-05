

var config_generator = new Vue({
  el: '#config_generator',
  data: {
    output_path: 'output',
    max_backup_files: 5,
    blogs: [
    	{
    		url: '',
    		client_secret: '',
    		username: '',
    		password: ''
    	}
    ],
    config: ''
  },
  methods: {

  	addBlog: function () {
  		var blog = {
  			url: '',
  			client_secret: '',
  			username: '',
  			password: ''
  		};
  		this.blogs.push(blog);
  	},

  	generateConfig: function () {

  		var data = this;

  		var config_string = '';

  		config_string += '{\n';

  		// settings
  		config_string += '    "settings": {\n';
  		config_string += '        "output_path": "' + this.output_path + '",\n';
  		config_string += '        "max_backup_files": ' + this.max_backup_files + '\n'
  		config_string += '    },\n'

  		// blogs
  		config_string += '   "blogs": [\n';

  		var total_blogs = data.blogs.length;
  		data.blogs.forEach(function (blog, index) {
  			
  			var comma = (index === total_blogs - 1) ? '' : ',';

  			config_string += '        {\n';
  			config_string += '            "url": "' + blog.url + '",\n';
  			config_string += '            "client_secret": "' + blog.client_secret + '",\n';
  			config_string += '            "username": "' + blog.username + '",\n';
  			config_string += '            "password": "' + blog.password + '"\n';
  			config_string += '        }' + comma + '\n';
  		});
  		config_string += '   ]\n'

  		config_string += '}';

  		data.config = config_string;
  	}
  }
});