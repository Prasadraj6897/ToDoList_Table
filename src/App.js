
import './App.css';
// import Increment_Decrement from "./components/increment_decrement_view"
// import Productlist from "./components/Productlist"

import {Provider} from "react-redux"
import {store} from "./redux_folder/store"
import  ContactAppREdux from "./components/contact_app_redux"
import Table_Task from "./components/Table_Task"

function App() {
  return (
    <div className="App">
      <Provider store = {store}>
        {/* <ContactAppREdux /> */}
        < Table_Task />
      </Provider>
      
    </div>
  );
}

export default App;
