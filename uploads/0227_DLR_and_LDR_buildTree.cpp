#include <iostream>
#include <stdlib.h>
using namespace std;

typedef struct TreeNode
{
    int value;
    struct TreeNode *leftChild;
    struct TreeNode *rightChild;
}TreeNode;

typedef struct Tree
{
    struct TreeNode *root;
}Tree;

int preOrder(TreeNode *node)
{
    if (node != NULL) {
        cout << node->value << endl;
        preOrder(node->leftChild);
        preOrder(node->rightChild);
    }
    return 0;
}

int inOrder(TreeNode *node)
{
    if (node != NULL) {
        inOrder(node->leftChild);
        cout << node->value << endl;
        inOrder(node->rightChild);
    }
}




TreeNode *newTreeNode(int value)
{
    TreeNode *p = (TreeNode*)malloc(sizeof(TreeNode));
    p->value = value;
    p->leftChild = NULL;
    p->rightChild = NULL;
    return p;
}


Tree *buildBinaryTree(TreeNode** node, int* DLR, int* LDR, int num)
{
    if (num == 1) {
        (*node) = newTreeNode(DLR[0]);
    } else if (num > 1){
        int leftNum = 0;
        int rightNum = 0;

        (*node) = newTreeNode(DLR[0]);

        /* 找到左子树节点的个数 */
        while (leftNum < num && DLR[0] != LDR[leftNum])
            leftNum++;

        /* 将左子树插入左节点 */
        buildBinaryTree(&(*node)->leftChild, DLR+1, LDR, leftNum);
        /* 将右子树插入右节点 */
        buildBinaryTree(&(*node)->rightChild, DLR+1+leftNum, LDR+1+leftNum, num-leftNum-1);
    }
}


int main(int argc, const char *argv[])
{
    int DLR[10] = {1,2,4,7,3,5,6,8};
    int LDR[10] = {4,7,2,1,5,3,8,6};

    Tree *tree = new Tree;
    buildBinaryTree(&tree->root, DLR, LDR, 8);

    preOrder(tree->root);
    cout << "===============" << endl;
    inOrder(tree->root);

    return 0;
}
