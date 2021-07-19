import * as React from "react";
import styled from "styled-components";
import { Card } from "react-bootstrap";
import { Button} from "react-bootstrap";
import logo from './download.png'

import {youtubeSearch, suggest} from "./services/youtube";

const Container = styled("div")`
  position: relative;
  width: 100%;
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  justify-content: center;
`;

const Container2 = styled("div")`
  width: 100%;
  display: flex;
  justify-content: center;
  padding-top: 10px;
`;

const CardsContainer = styled("div")`
  position: relative;
  width: 100%;
  display: flex;
  flex-flow: wrap;
  align-items: center;
  justify-content: center;
`; 

const SearchBox = styled("input")`
  box-sizing: border-box;
  height: 2.9rem;
  width: 100%;
  padding: 0.5rem;
  margin-top: 15px;
  padding-left: 1rem;
  border-radius: 0.2rem;
  border: 2px solid #aaa;
  max-width: 800px;
  font-size: 1rem;
`;

const Section = styled("section")`
  position: absolute;
  width: 95%;
  min-height: 18rem;
  max-width: 800px;
  height: auto;
  border: 1px solid #ddd;
  background-color: black;
  opacity: 0.85;
  border-top: none;
  border-radius: 5px;
  padding: 0.5rem;
  box-shadow: 1px 1px 1px #ddd;
  z-index: 1000;
`;
const SuggestionSpan = styled("span")`
  display: inline-block;
  width: 100%;
  color: white;
  font-weight: 800;
  margin-bottom: 0.5rem;
  margin-left: 0.5rem;
  cursor: pointer;
  z-index: 1000;
// `;

function Suggestions({ onSearch, items }) {
  if (!items || !items.length) {
    return null;
  }
  return (
    <Section>
      {items.map((item, key) => {
        return <SuggestionRow onSearch={onSearch} key={key} text={item} />;
      })}
    </Section>
  );
}

function SuggestionRow({ onSearch, text }) {
  return (
    <SuggestionSpan onClick={() => onSearch(text)}>
      {text}
    </SuggestionSpan>
  );
}

export default class FullSearchBox extends React.PureComponent{
    state = {
        suggestions: null,
        queryString : "",
        searchResult : [],
      //   searchResult : [
      //     {duration: "5:50", id: "x6kkDnL8-qw", thumbnail: "https://i.ytimg.com/vi/x6kkDnL8-qw/hq720.jpg?sqp=-…AFwAcABBg==&rs=AOn4CLB5TbXss5dfDZvPFq4SjP8LgQ8lYg", title: "Mussanje Maatu - Yenagali", view_count: "1.3M views"},
      //     {duration: "29:40", id: "8O26ZMp0PUo", thumbnail: "https://i.ytimg.com/vi/8O26ZMp0PUo/hq720.jpg?sqp=-…AFwAcABBg==&rs=AOn4CLBSxxs0pS_shixZFkE32-W6a22xeQ", title: "Mussanje Maatu I Kannada Movie Video Jukebox I Sudeep, Ramya", view_count: "5.5M views"}
      // ]
    };

    componentDidMount() {
      document.body.style.backgroundColor = "#1676c2"
    }
    
    render() {
        return (
            <>
            <Container>
              <img width="300px"src={logo} alt="Mp3juice.cc logo"/>
            </Container>
            <Container>
                <SearchBox
                onChange={e => this.onTypeSuggest(e.target.value)}
                onKeyPress={this.onKeyPress}
                placeholder="Search for music, songs, podcasts"
                value={this.state.queryString}
                type="search"
                />
            </Container>
            <Container2>
              <Suggestions onSearch={this.onSearch} items={this.state.suggestions} />
            </Container2>
            <Container2>
            </Container2>
            {this.renderCards()}
            </>
        )
    }


    renderCards() {
        return this.state.searchResult.map((result) => {
            const { title, id, thumbnail, duration, view_count } = result;
            const encodedYoutubeId = encodeURIComponent(id);
            const download_url = `api/youtube-dl/download?ybid=${encodedYoutubeId}`
            return (
              <CardsContainer>
                <Card 
                  style={{ 
                    width: '300px',
                    color: 'white',
                    marginBottom: '10px',
                    marginTop: '10px',
                    backgroundColor: '#2596be'
                  }}
                  key={id}
                  >
                    <img width="300px" src={thumbnail} alt={title} />
                    <h6>{title}</h6>
                    <p>{duration} mins | {view_count}</p>
                    <Button
                      style={{
                        color: 'white',
                        fontWeight: 'bold',
                        border: '2px solid white',
                        backgroundColor: '#0087cf'
                      }}
                      href={download_url}
                      target="_blank"
                      variant="outline-primary">Download</Button>
                </Card>
              </CardsContainer>
            );
        });
    }

    onTypeSuggest = async (
        queryString
        ) => {
        this.setState({ queryString: queryString })
        if (queryString.length < 2) {
            // search only after 2 chars
            this.setState({ suggestions: null })
            return null
        }
        suggest(queryString).then(list => this.setState({ suggestions: list }));
    }

    onKeyPress = event => {
      if (event.charCode === 13) {
        this.onSearch(event.target.value);
      }
    }

    // Make a search request for the current string
    onSearch = async (queryString) => {
      const searchResults = await youtubeSearch(queryString);
      this.setState({ 
        queryString : queryString,
        suggestions : null,
        searchResult : searchResults,
      });
    }
}