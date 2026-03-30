import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

export const sendChat = createAsyncThunk(
  "interaction/chat",
  async (message) => {
    const res = await axios.post("http://localhost:8000/chat", { message });
    return res.data;
  }
);

const slice = createSlice({
  name: "interaction",
  initialState: {
    messages: [],
  },
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(sendChat.fulfilled, (state, action) => {
      state.messages.push(action.payload.response);
    });
  },
});

export default slice.reducer;
