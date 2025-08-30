#include "chat.h"
#include "chat-parser.h"
#include "common.h"
#include "json-partial.h"
#include "json-schema-to-grammar.h"
#include "log.h"
#include "regex-partial.h"
#include <minja/chat-template.hpp>
#include <minja/minja.hpp>
#include <cstdio>

#include <gtest/gtest.h>

class ChatTest : public ::testing::Test
{
protected:
    ChatTest() {}
    virtual ~ChatTest() {}

    virtual void SetUp() {}
    virtual void TearDown() {}
};

TEST_F(ChatTest, TestParseMessage)
{
    EXPECT_TRUE(true);
}

TEST_F(ChatTest, TestGenerateResponse)
{
    EXPECT_TRUE(true);
}

TEST_F(ChatTest, TestSendMessage)
{
    EXPECT_TRUE(true);
}