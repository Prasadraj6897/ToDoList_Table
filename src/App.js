
import './App.css';
// import Increment_Decrement from "./components/increment_decrement_view"
import Productlist from "./components/Productlist"

import {Provider} from "react-redux"
import {store} from "./redux_folder/store"

function App() {
  return (
    <div className="App">
      <Provider store = {store}>
        <Productlist />
        {/* <Increment_Decrement /> */}
      </Provider>
      
    </div>
  );
}

export default App;
